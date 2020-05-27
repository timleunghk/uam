import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFlowComponent } from './request-flow.component';

describe('RequestFlowComponent', () => {
  let component: RequestFlowComponent;
  let fixture: ComponentFixture<RequestFlowComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestFlowComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestFlowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
