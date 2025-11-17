import {Component, OnInit} from '@angular/core';
import {API_BASE_URL} from '../../api-config';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Component({
  selector: 'app-generated-videos-list',
  standalone: false,
  templateUrl: './generated-videos-list.component.html',
  styleUrl: './generated-videos-list.component.css'
})
export class GeneratedVideosListComponent implements OnInit {
  videoUrls: { url: string; formattedDate: string }[] = [];
  errorMessage: string = '';
  selectedVideoUrl: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      this.errorMessage = 'Browser localStorage is not available.';
      return;
    }

    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');

    if (userId && token) {
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });

      this.http.get<{ latest_urls: { url: string; last_modified: string }[] }>(
        `${API_BASE_URL}/api/latest-videos-urls/${userId}`, { headers }
      ).subscribe({
        next: (response) => {
          this.videoUrls = response.latest_urls.map(video => ({
            url: video.url,
            formattedDate: this.formatDate(video.last_modified)
          }));
        },
        error: (err) => {
          this.errorMessage = err.error?.error || 'Failed to fetch video URLs.';
        }
      });
    } else {
      this.errorMessage = 'Missing user credentials.';
    }
  }

  formatDate(isoString: string): string {
    const date = new Date(isoString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    return `${hour}:${minute} ${day}.${month}.${year}`;
  }

  downloadVideo(url: string): void {
    fetch(url, { mode: 'cors' })
      .then(response => response.blob())
      .then(blob => {
        const blobUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = url.split('/').pop() || 'video.mp4';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(blobUrl);
      })
      .catch(() => {
        alert('Failed to download video.');
      });
  }
  deleteVideo(url: string, event: MouseEvent): void {
    event.stopPropagation();
    if (!confirm('Are you sure you want to delete this video?')) return;

    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');
    if (!userId || !token) {
      this.errorMessage = 'Missing user credentials.';
      return;
    }
    const videoKey = this.getS3KeyFromUrl(url);

    this.http.post<{ success: boolean; error?: string }>(
      `${API_BASE_URL}/api/delete-video`,
      { videoKey },
      { headers: { Authorization: `Bearer ${token}` } }
    ).subscribe({
      next: (response) => {
        if (response.success) {
          this.videoUrls = this.videoUrls.filter(video => video.url !== url);
          if (this.selectedVideoUrl === url) this.selectedVideoUrl = null;
        } else {
          this.errorMessage = response.error || 'Delete failed.';
        }
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Delete failed.';
      }
    });
  }

  getS3KeyFromUrl(url: string): string {

    const idx = url.indexOf('.com/');
    if (idx !== -1) {
      return url.substring(idx + 5);
    }
    return url;
  }

  toggleVideoPlayer(url: string): void {
    if (this.selectedVideoUrl === url) {
      this.selectedVideoUrl = null;
    } else {
      this.selectedVideoUrl = url;
    }
  }
}
