import { Component, OnInit, ViewChild } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { BaseRequest, Section } from '../../models/models';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Table } from 'primeng/table';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { LazyLoadEvent } from 'primeng/primeng';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.css'],
})

export class PasswordResetComponent implements OnInit {

  @ViewChild('dt', { static: true }) userTable: Table;
  @ViewChild('judDialog1', { static: true }) judDialog1: JudDialogComponent;
  @ViewChild('judDialog2', { static: false }) judDialog2: JudDialogComponent;
  selectedUser: BaseRequest;
  selectedUserLogin: string;
  searchForm: FormGroup;
  pwdForm: FormGroup;
  can_show: boolean = false;

  totalRecords: number;
  tableItems: any[];
  loading: boolean;
  allowLazyLoad: boolean = false;
  defaultSortField: string = 'uam_id';

  account_types: any[] = [{ id: '', value: 'ALL' }, { id: 1, value: 'JJO' }, { id: 2, value: 'Non-JJO' }, { id: 3, value: 'Special Account' }];
  // sections: any[] = [{ id: '', value: 'ALL' }, { id: 1, value: 'ITOO' }, { id: 2, value: 'ITOT' }, { id: 3, value: 'Finance' }];
  account_statuss: any[] = [{ id: '', value: 'ALL' }, { id: 0, value: 'Active' }, { id: 2, value: 'Deleted' }, { id: 1, value: 'Disabled' }];

  constructor(public data: DataService, private utils: UtilService, private _fb: FormBuilder) { }

  ngOnInit() {
    this.loading = true;
    this.userTable.first = 0;
    this.userTable.sortField = this.defaultSortField;
    this.userTable.sortOrder = 1;
    this.searchMain(1, 1, null, 1);

    this.searchForm = this._fb.group({
      win_login_name: [''],
      notes_mail: [''],
      account_type: [''],
      account_status: [''],
      post_title: [''],
      section: [''],
      surname: [''],
      givenname: [''],
      uam_id: [''],
    });

    this.pwdForm = this._fb.group({
      password: [''],
      password1: [''],
    });

    setTimeout(() => {
      this.onReset();
    }, 500);
  }

  loadTableLazy(event: LazyLoadEvent) {
    if (this.allowLazyLoad) {
      this.loading = true;
      let page = event.first / event.rows + 1;
      this.searchMain(0, page, event.sortField, event.sortOrder);
    }
  }

  onSearch() {
    // To avoid sending multiple requests to backend server when search button was pressed
    this.allowLazyLoad = false;
    this.userTable.first = 0;
    this.userTable.sortField = this.defaultSortField;
    this.userTable.sortOrder = 1;
    this.searchMain(0, 1, null, 1);
  }

  searchMain(show_all, page, sortField, sortOrder) {
    let searchObject = {};
    // searchObject['is_all'] = show_all;
    if (show_all == 0) {
      searchObject['win_login_name'] = this.searchForm.value['win_login_name'];
      searchObject['notes_mail'] = this.searchForm.value['notes_mail'];
      searchObject['account_type'] = this.searchForm.value['account_type'].id;
      // searchObject['account_status'] = this.searchForm.value['account_status'].id;
      searchObject['post_title'] = this.searchForm.value['post_title'];
      // searchObject['section'] = this.searchForm.value['section'].id;
      searchObject['section'] = (this.searchForm.value['section'] === null) ? null : this.searchForm.value['section'].code;
      searchObject['surname'] = this.searchForm.value['surname'];
      searchObject['givenname'] = this.searchForm.value['givenname'];
      searchObject['uam_id'] = this.searchForm.value['uam_id'];
    }
    searchObject['account_status'] = 0;
    searchObject['rows'] = this.userTable.rows;
    searchObject['page'] = page;
    // searchObject['sortField'] = sortField;
    // searchObject['sortOrder'] = sortOrder;
    if (sortField) {
      searchObject['ordering'] = ((sortOrder < 0) ? '-' : '') + sortField;
    }
    // this.data.getAllUserAccounts(searchObject).subscribe(
    this.data.getUserAccounts(searchObject, true).subscribe(
      data => {
        this.tableItems = data['results'];
        this.totalRecords = data['count'];
        this.loading = false;
        this.allowLazyLoad = true;
      }, error => {
        // this.judDialog1.showDialog('Search Error', this.utils.parseError(error), 'error', 'info');
        this.utils.promptError(error, 'Search Failed');
        this.loading = false;
        console.log(error.message);
      }
    )
  }

  onReset() {
    this.userTable.first = 0;
    //this.first = 0;
    //this.searchForm.reset();
    let controls = this.searchForm.controls;
    controls['account_type'].setValue(this.account_types[0]);
    // controls['account_status'].setValue(this.account_statuss[0]);
    // controls['section'].setValue(this.sections[0]);
    controls['section'].setValue(null);
    controls['win_login_name'].setValue('');
    controls['notes_mail'].setValue('');
    controls['post_title'].setValue('');
    controls['surname'].setValue('');
    controls['givenname'].setValue('');
    controls['uam_id'].setValue('');
  }

  onRowSelect(event) {
    this.selectedUser = event.data;
    let status = event.data['account_status'];
    if (status == 0) {
      this.selectedUserLogin = this.selectedUser['ad_windows_login_name'];
      this.can_show = true;
      this.pwdForm.controls['password'].setValue('');
      this.pwdForm.controls['password1'].setValue('');
    } else {
      this.judDialog1.showDialog('Information', 'User is not active!', 'warm', 'info');
    }
  }

  onRowUnselect(event) {
    this.selectedUser = null;
  }

  onCancel() {
    this.can_show = false;
  }

  onDialogClose() {
    this.can_show = false;
  }

  onDialogSubmit() {
    let pwd1 = this.pwdForm.value['password1'];

    var userObject = {};
    userObject['related_user'] = this.selectedUser.id;
    userObject['new_password'] = pwd1;

    this.judDialog2.showDialog('Information', 'The password is changing', 'wait', 'wait');
    this.data.chgPwd(userObject).subscribe(
      data => {
        this.judDialog2.showDialog('Information', 'The users password has been changed successfully', 'succ', 'info');
      }, error => {
        // this.judDialog2.showDialog('Password Change Error', this.utils.parseError(error), 'error', 'info');
        this.judDialog2.promptError(error, 'Password Change Failed');
      }
    )
  }

  onSubmit() {
    let pwd = this.pwdForm.value['password'];
    let pwd1 = this.pwdForm.value['password1'];
    if (pwd.length < 9 || pwd1.length < 9) {
      this.judDialog2.showDialog('Error', 'The mininum password length is 8!', 'error', 'info');
    } else if (pwd.match(pwd1) === null) {
      this.judDialog2.showDialog('Error', 'New Password and New Password (Re-entry) are not equal!', 'error', 'info');
    } else {
      this.judDialog2.showDialog('Confirmation', 'Are you sure to change the password?', 'confirm', 'confirmSub');
    }
  }

  keyDownFunction(event) {
    this.onSearch();
  }

  suggestedSection: Section[];
  clearSection(event: any) {
    this.searchForm.controls['section'].patchValue(null);
  }
  searchSections(event: any) {
    let query = event.query;
    let entered: string = event.query;
    this.data.searchSections(entered).subscribe(
      data => {
        this.suggestedSection = [];
        data.forEach((currentValue, idx, arr) => {
          this.suggestedSection.push(currentValue);
        })
      }, error => {
        this.utils.promptError(error, 'Cannot search sections');
        this.suggestedSection = [];
        console.log(error);
      }
    )
  }
}

