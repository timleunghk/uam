import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { RequestsUpdateAccountListComponent } from './requests-update-account-list.component';

describe('RequestsUpdateAccountListComponent', () => {
  let component: RequestsUpdateAccountListComponent;
  let fixture: ComponentFixture<RequestsUpdateAccountListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsUpdateAccountListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsUpdateAccountListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
