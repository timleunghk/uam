import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestPopupContainerComponent } from './request-popup-container.component';

describe('RequestPopupContainerComponent', () => {
  let component: RequestPopupContainerComponent;
  let fixture: ComponentFixture<RequestPopupContainerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestPopupContainerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestPopupContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
