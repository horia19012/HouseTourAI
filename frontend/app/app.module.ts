import {NgModule} from '@angular/core';
import {BrowserModule, provideClientHydration, withEventReplay} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {NavbarComponent} from './components/navbar/navbar.component';
import {GeneratePageComponent} from './components/generate-page/generate-page.component';
import {FormsModule} from '@angular/forms';
import {LoadingSpinnerComponent} from './components/loading-spinner/loading-spinner.component';
import {GeneratedVideoComponent} from './components/generated-video/generated-video.component';
import {LoginPageComponent} from './components/login-page/login-page.component';
import {ImageMatrixComponent} from './components/image-matrix/image-matrix.component';
import {HttpClientModule, provideHttpClient, withFetch} from '@angular/common/http';
import { UserNotifierComponent } from './components/user-notifier/user-notifier.component';
import { GeneratedVideosListComponent } from './components/generated-videos-list/generated-videos-list.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    GeneratePageComponent,
    LoadingSpinnerComponent,
    GeneratedVideoComponent,
    LoginPageComponent,
    ImageMatrixComponent,
    UserNotifierComponent,
    GeneratedVideosListComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [
    provideClientHydration(withEventReplay()),
    provideHttpClient(withFetch())
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
