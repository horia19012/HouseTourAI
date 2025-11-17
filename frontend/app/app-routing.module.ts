import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {GeneratePageComponent} from './components/generate-page/generate-page.component';
import {LoginPageComponent} from './components/login-page/login-page.component';
import {GeneratedVideosListComponent} from './components/generated-videos-list/generated-videos-list.component';
import {AuthGuard} from './auth.guard';

const routes: Routes = [
  {path: '', component: LoginPageComponent},
  {path: 'generate', component: GeneratePageComponent, canActivate: [AuthGuard]},
  {path: 'generated-videos', component: GeneratedVideosListComponent, canActivate: [AuthGuard]}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
