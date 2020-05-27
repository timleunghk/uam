import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestsDetailNewAccountExecuteComponent } from './requests-detail-account-execute.component';

describe('RequestsDetailNewAccountExecuteComponent', () => {
  let component: RequestsDetailNewAccountExecuteComponent;
  let fixture: ComponentFixture<RequestsDetailNewAccountExecuteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsDetailNewAccountExecuteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsDetailNewAccountExecuteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
