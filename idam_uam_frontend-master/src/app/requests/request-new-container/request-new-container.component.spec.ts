import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestNewContainerComponent } from './request-new-container.component';

describe('RequestNewContainerComponent', () => {
  let component: RequestNewContainerComponent;
  let fixture: ComponentFixture<RequestNewContainerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestNewContainerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestNewContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
