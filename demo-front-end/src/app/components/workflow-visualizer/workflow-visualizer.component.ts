import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WorkflowProgress } from '../../services/agent.service';

@Component({
  selector: 'app-workflow-visualizer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="workflow-container" *ngIf="progress">
      <div class="workflow-header">
        <h3>Agent Workflow Progress</h3>
        <div class="progress-info">
          <span class="progress-text">
            {{ progress.completedSteps }} / {{ progress.totalSteps }} steps completed
          </span>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              [style.width.%]="getProgressPercentage()">
            </div>
          </div>
        </div>
      </div>

      <div class="workflow-steps">
        <div 
          *ngFor="let step of progress.steps; let i = index" 
          class="step-item"
          [class.pending]="step.status === 'pending'"
          [class.in-progress]="step.status === 'in_progress'"
          [class.completed]="step.status === 'completed'"
          [class.error]="step.status === 'error'">
          
          <div class="step-indicator">
            <div class="step-number" *ngIf="step.status === 'pending'">{{ i + 1 }}</div>
            <div class="step-spinner" *ngIf="step.status === 'in_progress'">
              <div class="spinner"></div>
            </div>
            <div class="step-check" *ngIf="step.status === 'completed'">✓</div>
            <div class="step-error" *ngIf="step.status === 'error'">✗</div>
          </div>

          <div class="step-content">
            <div class="step-name">{{ step.name }}</div>
            <div class="step-timestamp">{{ formatTimestamp(step.timestamp) }}</div>
            <div class="step-data" *ngIf="step.data">
              <pre>{{ formatStepData(step.data) }}</pre>
            </div>
            <div class="step-error-message" *ngIf="step.error">
              Error: {{ step.error }}
            </div>
          </div>
        </div>
      </div>

      <div class="workflow-status" [class]="progress.status">
        <strong>Status:</strong> {{ getStatusText() }}
      </div>
    </div>
  `,
  styles: [`
    .workflow-container {
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      background: #f9f9f9;
      margin: 20px 0;
    }

    .workflow-header {
      margin-bottom: 20px;
    }

    .workflow-header h3 {
      margin: 0 0 10px 0;
      color: #333;
    }

    .progress-info {
      display: flex;
      align-items: center;
      gap: 15px;
    }

    .progress-text {
      min-width: 150px;
      font-size: 14px;
      color: #666;
    }

    .progress-bar {
      flex: 1;
      height: 8px;
      background: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #4CAF50, #2196F3);
      transition: width 0.3s ease;
    }

    .workflow-steps {
      margin: 20px 0;
    }

    .step-item {
      display: flex;
      align-items: flex-start;
      gap: 15px;
      padding: 15px;
      margin: 10px 0;
      border-radius: 6px;
      border-left: 4px solid;
      transition: all 0.3s ease;
    }

    .step-item.pending {
      background: #f5f5f5;
      border-left-color: #ccc;
    }

    .step-item.in-progress {
      background: #e3f2fd;
      border-left-color: #2196F3;
      animation: pulse 2s infinite;
    }

    .step-item.completed {
      background: #e8f5e8;
      border-left-color: #4CAF50;
    }

    .step-item.error {
      background: #ffebee;
      border-left-color: #f44336;
    }

    .step-indicator {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      flex-shrink: 0;
    }

    .step-number {
      background: #ccc;
      color: white;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
    }

    .step-spinner {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .spinner {
      width: 20px;
      height: 20px;
      border: 2px solid #f3f3f3;
      border-top: 2px solid #2196F3;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    .step-check {
      background: #4CAF50;
      color: white;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
    }

    .step-error {
      background: #f44336;
      color: white;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
    }

    .step-content {
      flex: 1;
    }

    .step-name {
      font-weight: 600;
      margin-bottom: 5px;
      color: #333;
    }

    .step-timestamp {
      font-size: 12px;
      color: #666;
      margin-bottom: 8px;
    }

    .step-data {
      background: white;
      padding: 10px;
      border-radius: 4px;
      border: 1px solid #e0e0e0;
      margin-top: 8px;
    }

    .step-data pre {
      margin: 0;
      font-size: 12px;
      color: #555;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .step-error-message {
      color: #f44336;
      font-size: 14px;
      margin-top: 5px;
      padding: 8px;
      background: #ffebee;
      border-radius: 4px;
      border-left: 3px solid #f44336;
    }

    .workflow-status {
      padding: 15px;
      border-radius: 6px;
      text-align: center;
      font-size: 16px;
      margin-top: 20px;
    }

    .workflow-status.started,
    .workflow-status.in_progress {
      background: #e3f2fd;
      color: #1976d2;
    }

    .workflow-status.completed {
      background: #e8f5e8;
      color: #388e3c;
    }

    .workflow-status.error {
      background: #ffebee;
      color: #d32f2f;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.02); }
      100% { transform: scale(1); }
    }
  `]
})
export class WorkflowVisualizerComponent {
  @Input() progress: WorkflowProgress | null = null;

  getProgressPercentage(): number {
    if (!this.progress) return 0;
    return (this.progress.completedSteps / this.progress.totalSteps) * 100;
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString();
  }

  formatStepData(data: any): string {
    if (typeof data === 'object') {
      return JSON.stringify(data, null, 2);
    }
    return String(data);
  }

  getStatusText(): string {
    if (!this.progress) return '';
    
    switch (this.progress.status) {
      case 'started': return 'Workflow Started';
      case 'in_progress': return 'Processing...';
      case 'completed': return 'Workflow Completed Successfully';
      case 'error': return 'Workflow Failed';
      default: return this.progress.status;
    }
  }
}