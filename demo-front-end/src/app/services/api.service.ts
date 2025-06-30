import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, Observer } from 'rxjs';
import { share, catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { fetchEventSource } from '@microsoft/fetch-event-source'

export interface ImageData {
  image_base64: string;
  filename: string;
}

export interface WorkflowRequest {
  images: ImageData[];
  job_context: string;
  enable_retry: boolean;
}

export interface StreamingResponse {
  status: string;
  step?: string;
  message?: string;
  result?: any;
  error?: string;
  success?: boolean;
  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8001';

  constructor(private http: HttpClient) { }

  streamWorkflow(request: WorkflowRequest): Observable<StreamingResponse> {
    const url = `${this.apiUrl}/api/v1/triage/workflow-stream`;

    return new Observable<StreamingResponse>((observer: Observer<StreamingResponse>) => {
      const controller = new AbortController();

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache'
        },
        body: JSON.stringify(request),
        signal: controller.signal
      })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        if (!response.body) {
          throw new Error('No response body available');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              observer.complete();
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');

            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  observer.next(data);
                } catch (error) {
                  console.error('Error parsing SSE data:', error);
                }
              }
            }
          }
        } catch (error) {
          if (!controller.signal.aborted) {
            observer.error(error);
          }
        }
      })
      .catch((error) => {
        if (!controller.signal.aborted) {
          observer.error(error);
        }
      });

      return () => {
        controller.abort();
      };
    }).pipe(
      share(),
      catchError((error) => {
        console.error('Streaming error:', error);
        return throwError(() => error);
      })
    );
  }

  streamWorkflowWithHttpClient(request: WorkflowRequest): Observable<StreamingResponse> {
    const url = `${this.apiUrl}/api/v1/triage/workflow-stream`;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache'
    });

    return new Observable<StreamingResponse>((observer) => {
      this.http.post(url, request, {
        headers,
        responseType: 'text',
        observe: 'response'
      }).subscribe({
        next: (_response) => {
          observer.error(new Error('HttpClient does not support Server-Sent Events streaming'));
        },
        error: (error) => {
          observer.error(error);
        }
      });
    }).pipe(
      catchError((error) => {
        console.error('Streaming error:', error);
        return throwError(() => error);
      })
    );
  }

  streamWorkflowWithEventSource(request: WorkflowRequest): Observable<StreamingResponse> {
    return new Observable<StreamingResponse>((observer) => {
      const params = new URLSearchParams({
        job_context: request.job_context,
        enable_retry: request.enable_retry.toString(),
      });

      const url = `${this.apiUrl}/api/v1/triage/workflow-stream-get?${params}`;
      const eventSource = new EventSource(url);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          observer.next(data);
        } catch (error) {
          console.error('Error parsing EventSource data:', error);
        }
      };

      eventSource.onerror = (error) => {
        observer.error(error);
        eventSource.close();
      };

      return () => {
        eventSource.close();
      };
    }).pipe(
      share(),
      catchError((error) => {
        console.error('EventSource streaming error:', error);
        return throwError(() => error);
      })
    );
  }


streamWorkflowWithFetchEventSource(request: WorkflowRequest): Observable<StreamingResponse> {
  return new Observable<StreamingResponse>((observer) => {
    const url = `${this.apiUrl}/api/v1/triage/workflow-stream`;

    const abortController = new AbortController();

    fetchEventSource(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
      signal: abortController.signal,

      onmessage: (event) => {
        try {
          const data = JSON.parse(event.data);
          observer.next(data);
        } catch (error) {
          observer.error(new Error('Failed to parse SSE data'));
        }
      },

      onerror: (error) => {
        observer.error(error);
        abortController.abort();
      },

      onclose: () => {
        observer.complete();
      }
    });

    return () => {
      abortController.abort();
    };
  }).pipe(
    catchError((error) => {
      console.error('Fetch EventSource streaming error:', error);
      return throwError(() => error);
    })
  );
}


  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  }

  generateRequestId(): string {
    return Math.random().toString(36).substring(2, 11);
  }
}
