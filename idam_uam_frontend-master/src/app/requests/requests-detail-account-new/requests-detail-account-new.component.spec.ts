import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestsDetailNewAccountComponent } from './requests-detail-account-new.component';

describe('RequestsDetailNewAccountComponent', () => {
  let component: RequestsDetailNewAccountComponent;
  let fixture: ComponentFixture<RequestsDetailNewAccountComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsDetailNewAccountComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsDetailNewAccountComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
