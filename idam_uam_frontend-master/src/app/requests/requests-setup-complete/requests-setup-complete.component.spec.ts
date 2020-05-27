import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestsSetupCompleteComponent } from './requests-setup-complete.component';

describe('RequestsSetupCompleteComponent', () => {
  let component: RequestsSetupCompleteComponent;
  let fixture: ComponentFixture<RequestsSetupCompleteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsSetupCompleteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsSetupCompleteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
