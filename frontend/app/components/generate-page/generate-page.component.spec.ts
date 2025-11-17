import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratePageComponent } from './generate-page.component';

describe('GeneratePageComponent', () => {
  let component: GeneratePageComponent;
  let fixture: ComponentFixture<GeneratePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [GeneratePageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
