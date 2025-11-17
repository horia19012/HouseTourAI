import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {API_BASE_URL} from '../../api-config';
import {UserNotifierComponent} from '../user-notifier/user-notifier.component';
import {WebsocketService} from '../../services/websocket.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-generate-page',
  standalone: false,
  templateUrl: './generate-page.component.html',
  styleUrls: ['./generate-page.component.css']
})
export class GeneratePageComponent implements OnInit {
  images: File[] = [];
  relations: string[] = [];
  isLoading = false;
  showGeneratedVideo = true;
  videoNamePrefix: string = '';
  @ViewChild(UserNotifierComponent) userNotifierComponent!: UserNotifierComponent;

  constructor(private http: HttpClient, private websocketService: WebsocketService) {
  }

  ngOnInit(): void {
    this.websocketService.onMessage().subscribe(event => {
      if (
        event.type === 'info'
      ) {
        this.isLoading = false;
      }
    });
    this.checkUploadThread();
  }

  checkUploadThread() {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');

    if (userId && token) {
      this.http.get<any>(`${API_BASE_URL}/debug/threads`, {
        headers: {Authorization: `Bearer ${token}`}
      }).subscribe({
        next: (res) => {
          const threadName = `UPLOAD_THREAD_${userId}`;
          this.isLoading = !!res.threads.find(
            (t: any) => t.name === threadName && t.alive
          );
        },
        error: (err) => {
          console.warn('Could not check upload thread', err);
          this.isLoading = false;
        }
      });
    }
  }

  handleImagesSelected(selectedFiles: File[]): void {
    this.images = selectedFiles;
    console.log('Received images:', this.images);
  }

  handleRelationsChange(updatedRelations: string[]): void {
    this.relations = updatedRelations;
    console.log('Updated Relations received in parent:', this.relations);
  }

  generateVideo(): void {
    this.isLoading = true;

    if (this.userNotifierComponent) {
      this.userNotifierComponent.clearProgress();
    }

    console.log('Images:', this.images);
    console.log('Relations:', this.relations);  // <-- Log relations

    const formData = new FormData();


    this.images.forEach((file, index) => {

      const renamedFile = new File([file], `${index + 1}.jpg`, {type: file.type});
      formData.append('images', renamedFile);
    });


    formData.append('relations', JSON.stringify(this.relations));

    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');

    if (userId) {
      formData.append('user_id', userId!);
    } else {
      console.warn('No user_id found in localStorage');
    }

    //had to send user local time because the local time on the ec2 is different from the users
    const localTimeLocalIso = new Date(
      new Date().getTime() - new Date().getTimezoneOffset() * 60000
    ).toISOString();
    formData.append('local_time', localTimeLocalIso);

    const namePrefix = this.videoNamePrefix?.trim() || 'final_output_';
    formData.append('video_name_prefix', namePrefix);

    this.http.post(`${API_BASE_URL}/api/upload`, formData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }).subscribe({
      next: (response) => {
        console.log('Server response:', response);
        this.isLoading = false;
        this.showGeneratedVideo = true;
      },
      error: (error) => {
        console.error('Error sending data to backend:', error);
        this.isLoading = false;
      }
    });

  }


  downloadFinalVideo(): void {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');

    if (!userId || !token) {
      console.error('Missing user ID or token in localStorage');
      return;
    }

    this.http.get(`${API_BASE_URL}/api/download/${userId}`, {
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${token}`
      }
    }).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'final_output.mp4';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Download failed:', err);

        if (err.error instanceof Blob) {
          err.error.text().then((text: string) => {
            console.log('Error body:', text);
          });
        }
      }
    });
  }

}
