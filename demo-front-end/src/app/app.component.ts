import { Component, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ImageUploadComponent } from './components/image-upload/image-upload.component';
import { WorkflowVisualizerComponent } from './components/workflow-visualizer/workflow-visualizer.component';
import { AgentService, WorkflowProgress } from './services/agent.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ImageUploadComponent, WorkflowVisualizerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'agent-demo';
  workflowProgress: WorkflowProgress | null = null;
  
  @ViewChild('uploadComponent') uploadComponent!: ImageUploadComponent;

  constructor(private agentService: AgentService) {
    this.agentService.getWorkflowProgress().subscribe(progress => {
      this.workflowProgress = progress;
      
      if (progress.status === 'completed' || progress.status === 'error') {
        setTimeout(() => {
          if (this.uploadComponent) {
            this.uploadComponent.setProcessing(false);
          }
        }, 100);
      }
    });
  }

  onImagesSelected(images: File[]) {
    console.log('Images selected:', images.length);
  }

  async onProcessStart() {
    if (this.uploadComponent && this.uploadComponent.selectedFiles.length > 0) {
      await this.agentService.processImages(this.uploadComponent.selectedFiles);
    }
  }
}
