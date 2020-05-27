import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FileMaintainerComponent } from './file-maintainer.component';

describe('FileMaintainerComponent', () => {
  let component: FileMaintainerComponent;
  let fixture: ComponentFixture<FileMaintainerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FileMaintainerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FileMaintainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
