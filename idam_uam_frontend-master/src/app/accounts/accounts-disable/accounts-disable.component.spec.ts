import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { AccountsDisableComponent } from './accounts-disable.component';

describe('DisableAccountComponent', () => {
  let component: AccountsDisableComponent;
  let fixture: ComponentFixture<AccountsDisableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AccountsDisableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AccountsDisableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
