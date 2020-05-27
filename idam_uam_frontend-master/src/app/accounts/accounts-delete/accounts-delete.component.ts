import { Component, OnInit, ViewChild } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { BaseRequest, Section } from '../../models/models';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Table } from 'primeng/table';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { LazyLoadEvent } from 'primeng/primeng';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-accounts-delete',
  templateUrl: './accounts-delete.component.html',
  styleUrls: ['./accounts-delete.component.css'],
})

export class AccountsDeleteComponent implements OnInit {

  @ViewChild('dt', { static: true }) userTable: Table;
  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;
  searchForm: FormGroup;
  delete_list: BaseRequest[] = [];

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
    searchObject['account_status'] = 1;
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
        this.utils.promptError(error, 'Search Error');
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
    this.delete_list = [];
  }

  onSelect(event) {
    this.delete_list.push(event);
  }

  onCancel(event) {
    this.delete_list.splice(this.delete_list.indexOf(event), 1);
  }

  showDeleteButton(request) {
    let isNotFoundInDelete = this.delete_list.find(x => x.id == request.id) == null;
    let isAccountDisable = (request.account_status == 1);
    return isNotFoundInDelete && isAccountDisable;
  }

  isShowSelectRow(request) {
    return true;
  }

  onConfirmDelete() {
    this.judDialog.showDialog('Confirmation', 'Are you sure to delete the users?', 'confirm', 'confirmSub');
  }

  onDialogSubmit() {
    let users = '';
    this.delete_list.forEach(element => {
      users += (users == '' ? '' : ',') + element['id'];
    });

    var userObject = {};
    userObject['user_ids'] = users;

    this.judDialog.showDialog('Information', 'The users are being deleted', 'wait', 'wait');
    this.data.deleteUserAccounts(userObject).subscribe(
      data => {
        this.judDialog.showDialog('Information', 'The users has been deleted successfully', 'succ', 'info');
        this.delete_list.forEach(element => {
          let id = element['id'];
          let deletedUser = this.tableItems.find(x => x.id == id);
          if (deletedUser) {
            let select_acc_status = this.searchForm.value['account_status'].value;
            if (select_acc_status == 'ALL') {
              deletedUser['account_status'] = 2;
              deletedUser['account_status_name'] = 'Deleted';
            } else {
              this.tableItems.splice(this.tableItems.indexOf(deletedUser), 1);
            }
          }
        });
        this.delete_list = [];
      }, error => {
        this.judDialog.promptError(error, 'Delete Error');
      }
    )
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
        this.utils.promptError(error, 'Cannot Search Sections');
        this.suggestedSection = [];
      }
    )
  }
}
