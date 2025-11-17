import {Component, EventEmitter, OnDestroy, OnInit, Output} from '@angular/core';
import {WebsocketService} from '../../services/websocket.service';
import {Subscription} from 'rxjs';
import {trigger, transition, style, animate} from '@angular/animations';

interface ImageProgress {
  [imgName: string]: number;
}

@Component({
  selector: 'app-user-notifier',
  templateUrl: './user-notifier.component.html',
  standalone: false,
  styleUrls: ['./user-notifier.component.css'],
  animations: [
    trigger('slideIn', [
      transition(':enter', [
        style({left: '-400px', opacity: 0}),
        animate('400ms ease', style({left: '20px', opacity: 1}))
      ])
    ])
  ]
})
export class UserNotifierComponent implements OnInit, OnDestroy {
  private messageSub!: Subscription;
  imageProgress: ImageProgress = {};

  messages: string[] = [];
  queueMessages: string[] = [];
  warningMessages: string[] = [];
  infoMessages: string[] = [];

  @Output() infoReceived = new EventEmitter<void>();

  constructor(private wsService: WebsocketService) {
  }

  ngOnInit(): void {
    let userId: string | null = null;
    if (typeof window !== 'undefined' && window.localStorage) {
      userId = localStorage.getItem('user_id');
    }

    if (userId && !this.wsService.isCurrentlyConnected()) {
      this.wsService.connect(userId);
    }

    this.messageSub = this.wsService.onMessage().subscribe({
      next: (event: any) => {
        const {type, payload} = event;
        const text = payload.msg || payload;

        if (type === 'warning') {
          console.warn('Warning received:', text);
          this.warningMessages.push(text);
          return;
        }

        if (type === 'info') {
          console.info('Info received:', text);
          this.infoReceived.emit();
          this.clearProgress();
          this.infoMessages.push(text);
          return;
        }

        const progressMatch = text.match(/Processing\s+(\S+):\s+(\d+)%/);
        if (progressMatch) {
          const [_, imgName, percentStr] = progressMatch;
          const percent = parseInt(percentStr, 10);
          this.imageProgress[imgName] = percent;
        } else {
          this.messages.push(text);
        }
      }
    });
  }



  ngOnDestroy(): void {
    if (this.messageSub) this.messageSub.unsubscribe();
  }

  clearProgress(): void {
    this.imageProgress = {};
    this.messages = [];
    this.queueMessages = [];
    this.warningMessages = [];
    this.infoMessages = [];
  }

  dismissWarning(index: number): void {
    this.warningMessages.splice(index, 1);
  }

  dismissInfo(index: number): void {
    this.infoMessages.splice(index, 1);
  }

}
