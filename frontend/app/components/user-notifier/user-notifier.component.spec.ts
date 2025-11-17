import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserNotifierComponent } from './user-notifier.component';

describe('UserNotifierComponent', () => {
  let component: UserNotifierComponent;
  let fixture: ComponentFixture<UserNotifierComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UserNotifierComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserNotifierComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
