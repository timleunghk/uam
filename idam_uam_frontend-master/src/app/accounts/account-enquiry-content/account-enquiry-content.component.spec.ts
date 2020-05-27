import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AccountEnquiryContentComponent } from './account-enquiry-content.component';

describe('AccountEnquiryContentComponent', () => {
  let component: AccountEnquiryContentComponent;
  let fixture: ComponentFixture<AccountEnquiryContentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AccountEnquiryContentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AccountEnquiryContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
