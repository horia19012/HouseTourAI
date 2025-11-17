import {Injectable} from '@angular/core';
import {io, Socket} from 'socket.io-client';
import {Observable, BehaviorSubject} from 'rxjs';
import {API_BASE_URL} from '../api-config';

interface SubscribePayload {
  user_id: string;
}

@Injectable({
  providedIn: 'root',
})
export class WebsocketService {
  private socket!: Socket;
  private readonly url = API_BASE_URL;
  private connected$ = new BehaviorSubject<boolean>(false);

  constructor() {
  }


  connect(userId: string): void {
    if (this.socket && this.socket.connected) {
      console.log('[WebSocket] Already connected');
      return;
    }

    this.socket = io(this.url, {
      transports: ['websocket'],
      autoConnect: false,
      path: '/socket.io',
      query: {user_id: userId}
    });

    this.cleanSocketListeners();

    // Connect socket
    this.socket.connect();

    this.socket.on('connect', () => {
      console.log('[WebSocket] Socket connected:', this.socket.id);
      this.subscribeUser(userId);
      this.connected$.next(true);
    });

    this.socket.on('disconnect', (reason: string) => {
      console.warn('[WebSocket] Disconnected:', reason);
      this.connected$.next(false);
    });

    this.socket.on('subscribed', (data: any) => {
      console.log('[WebSocket] Subscription confirmed:', data);
    });

    this.socket.on('error', (error: any) => {
      console.error('[WebSocket] Error:', error);
    });
  }

  private cleanSocketListeners() {
    if (this.socket) {
      this.socket.off('connect');
      this.socket.off('disconnect');
      this.socket.off('subscribed');
      this.socket.off('error');
    }
  }

  private subscribeUser(userId: string): void {
    if (this.socket && this.socket.connected) {
      console.log('[WebSocket] Emitting subscribe for user:', userId);
      this.socket.emit('subscribe', {user_id: userId});
    } else {
      console.warn('[WebSocket] Cannot subscribe, socket not connected');
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.connected$.next(false);
    }
  }

  onMessage(): Observable<any> {
    return new Observable((observer) => {
      if (!this.socket) {
        console.error('[onMessage] Socket not initialized');
        observer.error('Socket not connected');
        return;
      }

      if (!this.socket.connected) {
        console.warn('[onMessage] Socket exists but is not connected');
      }

      console.log('[onMessage] Setting up message, warning, and info listeners');

      const messageHandler = (data: any) => {
        console.log('[onMessage] Received message:', data);
        observer.next({ type: 'message', payload: data });
      };

      const warningHandler = (data: any) => {
        console.warn('[onMessage] Received warning:', data);
        observer.next({ type: 'warning', payload: data });
      };

      const infoHandler = (data: any) => {
        console.info('[onMessage] Received info:', data);
        observer.next({ type: 'info', payload: data });
      };

      this.socket.on('message', messageHandler);
      this.socket.on('warning', warningHandler);
      this.socket.on('info', infoHandler);

      return () => {
        console.log('[onMessage] Cleaning up listeners');
        this.socket.off('message', messageHandler);
        this.socket.off('warning', warningHandler);
        this.socket.off('info', infoHandler);
      };
    });
  }


  isCurrentlyConnected(): boolean {
    return this.socket ? this.socket.connected : false;
  }

}
