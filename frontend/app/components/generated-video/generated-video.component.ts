import {AfterViewInit, Component, ElementRef, Input, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {API_BASE_URL} from '../../api-config';
import {HttpClient} from '@angular/common/http';

@Component({
  selector: 'app-generated-video',
  standalone: false,
  templateUrl: './generated-video.component.html',
  styleUrl: './generated-video.component.css'
})
export class GeneratedVideoComponent implements OnInit, AfterViewInit, OnDestroy {
  videoUrl: string = '';
  isPaused: boolean = true;
  @Input() isVisible: boolean = false;

  @ViewChild('videoElement') videoRef!: ElementRef<HTMLVideoElement>;

  private playHandler = () => {
    this.isPaused = false;
  };
  private pauseHandler = () => {
    this.isPaused = true;
  };

  constructor(private http: HttpClient) {
  }

  ngOnInit(): void {
    this.isPaused = false;
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');
    if (userId && token) {
      this.http.get<{ videoUrl: string }>(`${API_BASE_URL}/api/latest-video/${userId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }).subscribe(response => {
        this.videoUrl = response.videoUrl;
      });
    }
  }

  ngAfterViewInit(): void {
    const video = this.videoRef?.nativeElement;
    if (video) {
      video.addEventListener('play', this.playHandler);
      video.addEventListener('pause', this.pauseHandler);
      this.isPaused = video.paused;
    }
  }

  ngOnDestroy(): void {
    const video = this.videoRef?.nativeElement;
    if (video) {
      video.removeEventListener('play', this.playHandler);
      video.removeEventListener('pause', this.pauseHandler);
    }
  }

  togglePlay(event: MouseEvent) {
    this.isPaused = false;
    console.log(this.isPaused)
    event.stopPropagation();
    const video = this.videoRef.nativeElement;
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  }

  pauseVideo(event: MouseEvent) {
    this.isPaused = true;
    event.stopPropagation();
    const video = this.videoRef.nativeElement;
    video.pause();
  }

  closeVideo() {
    const video = this.videoRef.nativeElement;
    video.pause();
    this.isVisible = false;
  }

  showVideo() {
    this.isVisible = true;
    setTimeout(() => {
      const video = this.videoRef.nativeElement;
      video.play();
    }, 0);
  }
}
