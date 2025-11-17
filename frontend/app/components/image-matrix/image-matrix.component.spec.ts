import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageMatrixComponent } from './image-matrix.component';

describe('ImageMatrixComponent', () => {
  let component: ImageMatrixComponent;
  let fixture: ComponentFixture<ImageMatrixComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ImageMatrixComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ImageMatrixComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
