import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestsToDoListComponent } from './requests-todolist.component';

describe('RequestsToDoListComponent', () => {
  let component: RequestsToDoListComponent;
  let fixture: ComponentFixture<RequestsToDoListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestsToDoListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestsToDoListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
