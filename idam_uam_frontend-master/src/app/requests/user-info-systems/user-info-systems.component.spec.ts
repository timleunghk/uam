import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UserInfoSystemsComponent } from './user-info-systems.component';

describe('UserInfoSystemsComponent', () => {
  let component: UserInfoSystemsComponent;
  let fixture: ComponentFixture<UserInfoSystemsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UserInfoSystemsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UserInfoSystemsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
