import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestsDetailNewAccountReviewComponent } from './requests-detail-account-review.component';

describe('RequestsDetailNewAccountReviewComponent', () => {
  let component: RequestsDetailNewAccountReviewComponent;
  let fixture: ComponentFixture<RequestsDetailNewAccountReviewComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsDetailNewAccountReviewComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsDetailNewAccountReviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
