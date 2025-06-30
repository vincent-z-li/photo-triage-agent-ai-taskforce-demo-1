import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-image-upload',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="upload-container">
      <div class="upload-area" 
           (click)="fileInput.click()"
           (dragover)="onDragOver($event)"
           (dragleave)="onDragLeave($event)"
           (drop)="onDrop($event)"
           [class.drag-over]="isDragOver">
        
        <input #fileInput 
               type="file" 
               multiple 
               accept="image/*" 
               (change)="onFileSelect($event)"
               style="display: none;">
        
        <div class="upload-content">
          <div class="upload-icon">📁</div>
          <div class="upload-text">
            <h3>Upload Images for Triage</h3>
            <p>Drag and drop images here or click to select</p>
            <p class="upload-hint">Supports: JPG, PNG, GIF (max 10 files)</p>
          </div>
        </div>
      </div>

      <div class="selected-files" *ngIf="selectedFiles.length > 0">
        <h4>Selected Files ({{ selectedFiles.length }})</h4>
        <div class="file-grid">
          <div *ngFor="let file of selectedFiles; let i = index" class="file-item">
            <div class="file-preview">
              <img [src]="getFilePreview(file)" alt="Preview">
            </div>
            <div class="file-info">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-size">{{ formatFileSize(file.size) }}</div>
            </div>
            <button class="remove-file" (click)="removeFile(i)">×</button>
          </div>
        </div>
        
        <div class="upload-actions">
          <button class="btn btn-primary" 
                  (click)="processImages()"
                  [disabled]="isProcessing">
            <span *ngIf="!isProcessing">Start Triage Workflow</span>
            <span *ngIf="isProcessing">Processing...</span>
          </button>
          <button class="btn btn-secondary" 
                  (click)="clearFiles()"
                  [disabled]="isProcessing">
            Clear All
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .upload-container {
      margin: 20px 0;
    }

    .upload-area {
      border: 2px dashed #ccc;
      border-radius: 8px;
      padding: 40px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      background: #fafafa;
    }

    .upload-area:hover {
      border-color: #2196F3;
      background: #f0f8ff;
    }

    .upload-area.drag-over {
      border-color: #4CAF50;
      background: #f1f8e9;
      transform: scale(1.02);
    }

    .upload-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
    }

    .upload-icon {
      font-size: 48px;
      opacity: 0.6;
    }

    .upload-text h3 {
      margin: 0 0 10px 0;
      color: #333;
    }

    .upload-text p {
      margin: 5px 0;
      color: #666;
    }

    .upload-hint {
      font-size: 14px;
      color: #999 !important;
    }

    .selected-files {
      margin-top: 30px;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      background: white;
    }

    .selected-files h4 {
      margin: 0 0 20px 0;
      color: #333;
    }

    .file-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 15px;
      margin-bottom: 20px;
    }

    .file-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      background: #f9f9f9;
      position: relative;
    }

    .file-preview {
      width: 50px;
      height: 50px;
      border-radius: 4px;
      overflow: hidden;
      flex-shrink: 0;
    }

    .file-preview img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .file-info {
      flex: 1;
      min-width: 0;
    }

    .file-name {
      font-weight: 500;
      margin-bottom: 2px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .file-size {
      font-size: 12px;
      color: #666;
    }

    .remove-file {
      position: absolute;
      top: 5px;
      right: 5px;
      width: 20px;
      height: 20px;
      border: none;
      background: #f44336;
      color: white;
      border-radius: 50%;
      cursor: pointer;
      font-size: 14px;
      line-height: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .remove-file:hover {
      background: #d32f2f;
    }

    .upload-actions {
      display: flex;
      gap: 15px;
      justify-content: center;
      margin-top: 20px;
    }

    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s ease;
      font-weight: 500;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-primary {
      background: #2196F3;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #1976D2;
    }

    .btn-secondary {
      background: #666;
      color: white;
    }

    .btn-secondary:hover:not(:disabled) {
      background: #555;
    }
  `]
})
export class ImageUploadComponent {
  @Output() imagesSelected = new EventEmitter<File[]>();
  @Output() processStart = new EventEmitter<void>();

  selectedFiles: File[] = [];
  isDragOver = false;
  isProcessing = false;
  filePreviews: { [key: string]: string } = {};

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    
    const files = Array.from(event.dataTransfer?.files || []);
    this.handleFiles(files);
  }

  onFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    this.handleFiles(files);
  }

  private handleFiles(files: File[]) {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
      alert('Please select only image files');
      return;
    }

    if (this.selectedFiles.length + imageFiles.length > 10) {
      alert('Maximum 10 files allowed');
      return;
    }

    this.selectedFiles.push(...imageFiles);
    
    // Generate previews
    imageFiles.forEach(file => {
      this.generatePreview(file);
    });

    this.imagesSelected.emit(this.selectedFiles);
  }

  private generatePreview(file: File) {
    const reader = new FileReader();
    reader.onload = (e) => {
      this.filePreviews[file.name] = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  getFilePreview(file: File): string {
    return this.filePreviews[file.name] || '';
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  removeFile(index: number) {
    const removedFile = this.selectedFiles.splice(index, 1)[0];
    delete this.filePreviews[removedFile.name];
    this.imagesSelected.emit(this.selectedFiles);
  }

  clearFiles() {
    this.selectedFiles = [];
    this.filePreviews = {};
    this.imagesSelected.emit(this.selectedFiles);
  }

  processImages() {
    if (this.selectedFiles.length === 0) {
      alert('Please select at least one image');
      return;
    }

    this.isProcessing = true;
    this.processStart.emit();
  }

  setProcessing(processing: boolean) {
    this.isProcessing = processing;
  }
}