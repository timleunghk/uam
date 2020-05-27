import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AccountsEnquiryListComponent } from './accounts-enquiry-list.component';

describe('EnableAccountComponent', () => {
  let component: AccountsEnquiryListComponent;
  let fixture: ComponentFixture<AccountsEnquiryListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AccountsEnquiryListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AccountsEnquiryListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
