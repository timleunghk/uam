import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AccountsEnableComponent } from './accounts-enable.component';

describe('EnableAccountComponent', () => {
  let component: AccountsEnableComponent;
  let fixture: ComponentFixture<AccountsEnableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AccountsEnableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AccountsEnableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
