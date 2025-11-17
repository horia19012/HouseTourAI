import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {API_BASE_URL} from '../../api-config';
import {WebsocketService} from '../../services/websocket.service';

@Component({
  selector: 'app-login-page',
  standalone: false,
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
})
export class LoginPageComponent {
  isLogin: boolean = true;

  constructor(private router: Router, private http: HttpClient) {
  }

  loginData = {
    email: '',
    password: ''
  };

  registerData = {
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  };

  switchToRegister() {
    this.isLogin = false;
  }

  switchToLogin() {
    this.isLogin = true;
  }

  onLoginSubmit() {
    this.http.post(`${API_BASE_URL}/api/login`, this.loginData).subscribe(
      (res: any) => {
        console.log('Login success', res);
        localStorage.setItem('token', res.token);
        localStorage.setItem('user_id', res.user_id);

        this.router.navigate(['/generate']);
      },
      err => console.error('Login failed', err)
    );
  }

  onRegisterSubmit() {
    if (this.registerData.password !== this.registerData.confirmPassword) {
      alert('Passwords do not match!');
      return;
    }

    this.http.post(`${API_BASE_URL}/api/register`, this.registerData).subscribe({
      next: (res) => {
        console.log('Register success', res);
        alert('Registered successfully');
        this.isLogin = true;
      },
      error: (err) => {
        console.error('Register failed', err);
        alert('Registration failed: ' + (err.error?.error || 'Unknown error'));
      }
    });
  }
}
