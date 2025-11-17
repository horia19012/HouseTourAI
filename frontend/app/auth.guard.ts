import {CanActivate, Router} from '@angular/router';
import {Injectable} from '@angular/core';
import {API_BASE_URL} from './api-config';
import {catchError, map, Observable, of} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router, private http: HttpClient) {
  }

  canActivate(): Observable<boolean> {
    const token = localStorage.getItem('token');
    if (!token) {
      this.router.navigate(['']);
      return of(false);
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${API_BASE_URL}/api/auth/validate-token`, {headers}).pipe(
      map(() => true),
      catchError(() => {
        this.router.navigate(['']);
        return of(false);
      })
    );
  }
}
