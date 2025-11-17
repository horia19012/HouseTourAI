import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratedVideosListComponent } from './generated-videos-list.component';

describe('GeneratedVideosListComponent', () => {
  let component: GeneratedVideosListComponent;
  let fixture: ComponentFixture<GeneratedVideosListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [GeneratedVideosListComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratedVideosListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
