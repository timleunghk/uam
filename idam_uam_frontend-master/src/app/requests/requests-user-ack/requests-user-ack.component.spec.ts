import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestsUserAckComponent } from './requests-user-ack.component';

describe('RequestsUserAckComponent', () => {
  let component: RequestsUserAckComponent;
  let fixture: ComponentFixture<RequestsUserAckComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsUserAckComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsUserAckComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
