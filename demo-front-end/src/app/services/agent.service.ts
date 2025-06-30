import { Injectable, OnDestroy } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { ApiService, WorkflowRequest, ImageData, StreamingResponse } from './api.service';
import { takeUntil, finalize } from 'rxjs/operators';

export interface WorkflowStep {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  timestamp: string;
  data?: any;
  error?: string;
}

export interface WorkflowProgress {
  requestId: string;
  currentStep: string;
  totalSteps: number;
  completedSteps: number;
  steps: WorkflowStep[];
  status: 'started' | 'in_progress' | 'completed' | 'error';
}

@Injectable({
  providedIn: 'root'
})
export class AgentService implements OnDestroy {
  private workflowProgress$ = new Subject<WorkflowProgress>();
  private destroy$ = new Subject<void>();

  constructor(private apiService: ApiService) { }

  getWorkflowProgress(): Observable<WorkflowProgress> {
    return this.workflowProgress$.asObservable();
  }

  async processImages(images: File[]): Promise<void> {
    const requestId = this.apiService.generateRequestId();

    const initialProgress: WorkflowProgress = {
      requestId,
      currentStep: 'initialize',
      totalSteps: 5,
      completedSteps: 0,
      steps: [
        { id: '1', name: 'Initialize Processing', status: 'pending', timestamp: new Date().toISOString() },
        { id: '2', name: 'Quality Analysis', status: 'pending', timestamp: new Date().toISOString() },
        { id: '3', name: 'Photo Classification', status: 'pending', timestamp: new Date().toISOString() },
        { id: '4', name: 'ReAct Reflection', status: 'pending', timestamp: new Date().toISOString() },
        { id: '5', name: 'Generate Feedback', status: 'pending', timestamp: new Date().toISOString() }
      ],
      status: 'started'
    };

    this.workflowProgress$.next(initialProgress);

    try {
      const imageData: ImageData[] = await Promise.all(
        images.map(async (file) => ({
          image_base64: await this.apiService.fileToBase64(file),
          filename: file.name
        }))
      );

      const workflowRequest: WorkflowRequest = {
        images: imageData,
        job_context: "Photo triage demo",
        enable_retry: true
      };

      this.apiService.streamWorkflowWithFetchEventSource(workflowRequest)
        .pipe(
          takeUntil(this.destroy$),
          finalize(() => {
            console.log('Workflow stream completed');
          })
        )
        .subscribe({
          next: (data: StreamingResponse) => {
            this.updateWorkflowProgress(data, initialProgress);
          },
          error: (error) => {
            console.error('Workflow streaming error:', error);
            const errorProgress = { ...initialProgress };
            errorProgress.status = 'error';
            const currentStepIndex = errorProgress.steps.findIndex(s => s.status === 'in_progress');
            if (currentStepIndex >= 0) {
              errorProgress.steps[currentStepIndex].status = 'error';
              errorProgress.steps[currentStepIndex].error = error.message || 'Streaming error';
            } else {
              errorProgress.steps[0].status = 'error';
              errorProgress.steps[0].error = error.message || 'Streaming error';
            }
            this.workflowProgress$.next(errorProgress);
          },
          complete: () => {
            console.log('Workflow stream completed successfully');
          }
        });

    } catch (error) {
      console.error('Workflow initialization error:', error);
      const errorProgress = { ...initialProgress };
      errorProgress.status = 'error';
      errorProgress.steps[0].status = 'error';
      errorProgress.steps[0].error = error instanceof Error ? error.message : 'Unknown error';
      this.workflowProgress$.next(errorProgress);
    }
  }

  private updateWorkflowProgress(data: any, currentProgress: WorkflowProgress): void {
    const updatedProgress = { ...currentProgress };

    updatedProgress.steps.forEach(step => {
      if (step.status === 'in_progress') {
        step.timestamp = new Date().toISOString();
      }
    });

    switch (data.status) {
      case 'started':
        updatedProgress.steps[0].status = 'in_progress';
        updatedProgress.status = 'in_progress';
        updatedProgress.currentStep = 'initialize';
        break;

      case 'processing':
        this.handleProcessingStep(data, updatedProgress);
        break;

      case 'step_completed':
        this.handleStepCompleted(data, updatedProgress);
        break;

      case 'result':
        updatedProgress.steps.forEach(step => {
          if (step.status === 'in_progress') step.status = 'completed';
        });
        updatedProgress.completedSteps = updatedProgress.totalSteps;
        updatedProgress.status = 'completed';

        if (data.final_feedback) {
          updatedProgress.steps[4].data = data.final_feedback;
        }
        break;

      case 'error':
        updatedProgress.status = 'error';
        const currentStepIndex = updatedProgress.steps.findIndex(s => s.status === 'in_progress');
        if (currentStepIndex >= 0) {
          updatedProgress.steps[currentStepIndex].status = 'error';
          updatedProgress.steps[currentStepIndex].error = data.error || data.message;
        }
        break;
    }

    this.workflowProgress$.next(updatedProgress);
  }

  private handleProcessingStep(data: any, progress: WorkflowProgress): void {
    switch (data.step) {
      case 'initialize':
        progress.steps[0].status = 'in_progress';
        progress.currentStep = 'initialize';
        break;
      case 'quality_analysis':
        progress.steps[0].status = 'completed';
        progress.steps[1].status = 'in_progress';
        progress.completedSteps = 1;
        progress.currentStep = 'quality_analysis';
        break;
      case 'classification':
        progress.steps[1].status = 'completed';
        progress.steps[2].status = 'in_progress';
        progress.completedSteps = 2;
        progress.currentStep = 'classification';
        break;
      case 'reflection':
        progress.steps[2].status = 'completed';
        progress.steps[3].status = 'in_progress';
        progress.completedSteps = 3;
        progress.currentStep = 'reflection';
        break;
      case 'retry_preparation':
      case 'retry_analysis':
        progress.currentStep = 'reflection';
        break;
      case 'feedback':
        progress.steps[3].status = 'completed';
        progress.steps[4].status = 'in_progress';
        progress.completedSteps = 4;
        progress.currentStep = 'feedback';
        break;
    }
  }

  private handleStepCompleted(data: any, progress: WorkflowProgress): void {
    let stepIndex = -1;

    switch (data.step) {
      case 'quality_analysis':
        stepIndex = 1;
        break;
      case 'classification':
        stepIndex = 2;
        break;
      case 'reflection':
        stepIndex = 3;
        break;
      case 'retry_analysis':
        stepIndex = 2;
        break;
      case 'feedback':
        stepIndex = 4;
        break;
    }

    if (stepIndex >= 0 && stepIndex < progress.steps.length) {
      progress.steps[stepIndex].status = 'completed';
      progress.steps[stepIndex].data = data.result;
      progress.steps[stepIndex].timestamp = new Date().toISOString();
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  cancelWorkflow(): void {
    this.destroy$.next();
  }
}
