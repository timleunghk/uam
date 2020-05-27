import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AccountsDeleteComponent } from './accounts-delete.component';

describe('EnableAccountComponent', () => {
  let component: AccountsDeleteComponent;
  let fixture: ComponentFixture<AccountsDeleteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AccountsDeleteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AccountsDeleteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
