import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PersonalProfilesComponent } from './personal-profiles.component';

describe('EnableAccountComponent', () => {
  let component: PersonalProfilesComponent;
  let fixture: ComponentFixture<PersonalProfilesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PersonalProfilesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PersonalProfilesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
