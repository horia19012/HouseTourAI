import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {WebsocketService} from '../../services/websocket.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css'],
  standalone: false
})
export class NavbarComponent {

  constructor(private router: Router, private wsService: WebsocketService) {
  }

  onGenerateVideo() {
    this.router.navigate(['/generate']);
  }

  onGeneratedVideos() {
    this.router.navigate(['/generated-videos']);
  }

  onLogout() {
    console.log('Logout clicked');
    localStorage.clear();

    this.wsService.disconnect();

    this.router.navigate(['/']);
  }
}
