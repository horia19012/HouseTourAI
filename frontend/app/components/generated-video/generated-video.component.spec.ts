import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratedVideoComponent } from './generated-video.component';

describe('GeneratedVideoComponent', () => {
  let component: GeneratedVideoComponent;
  let fixture: ComponentFixture<GeneratedVideoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [GeneratedVideoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratedVideoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
