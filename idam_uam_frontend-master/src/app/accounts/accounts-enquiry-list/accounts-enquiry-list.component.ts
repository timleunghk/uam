import { Component, OnInit, ViewChild } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { BaseRequest, Section } from '../../models/models';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Table } from 'primeng/table';
import { CommunicationService } from '../../judCommon/communication.service';
import { LazyLoadEvent } from 'primeng/primeng';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-accounts-enquiry-list',
  templateUrl: './accounts-enquiry-list.component.html',
  styleUrls: ['./accounts-enquiry-list.component.css'],
  providers: [CommunicationService],
})

export class AccountsEnquiryListComponent implements OnInit {

  @ViewChild('dt', { static: true }) userTable: Table;
  selectedItem: BaseRequest;
  searchForm: FormGroup;

  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;

  totalRecords: number;
  tableItems: any[];
  loading: boolean;
  allowLazyLoad: boolean = false;
  defaultSortField: string = 'uam_id';

  account_types: any[] = [{ id: '', value: 'ALL' }, { id: 1, value: 'JJO' }, { id: 2, value: 'Non-JJO' }, { id: 3, value: 'Special Account' }];
  sections: any[] = [{ id: '', value: 'ALL' }, { id: 1, value: 'ITOO' }, { id: 2, value: 'ITOT' }, { id: 3, value: 'Finance' }];
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
      searchObject['account_status'] = this.searchForm.value['account_status'].id;
      searchObject['post_title'] = this.searchForm.value['post_title'];
      // searchObject['section'] = this.searchForm.value['section'].id;
      searchObject['section'] = (this.searchForm.value['section'] === null) ? null : this.searchForm.value['section'].code;
      searchObject['surname'] = this.searchForm.value['surname'];
      searchObject['givenname'] = this.searchForm.value['givenname'];
      searchObject['uam_id'] = this.searchForm.value['uam_id'];
    }

    searchObject['rows'] = this.userTable.rows;
    searchObject['page'] = page;
    // searchObject['sortField'] = sortField;
    // searchObject['sortOrder'] = sortOrder;   
    if (sortField) {
      searchObject['ordering'] = ((sortOrder < 0) ? '-' : '') + sortField;
    }
    // this.data.getAllUserAccounts(searchObject).subscribe(      
    this.data.getUserAccounts(searchObject).subscribe(
      data => {
        this.tableItems = data['results'];
        this.totalRecords = data['count'];
        this.loading = false;
        this.allowLazyLoad = true;
      }, error => {
        // this.judDialog.showDialog('Search Error', this.utils.parseError(error), 'error', 'info');
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
    controls['account_status'].setValue(this.account_statuss[0]);
    // controls['section'].setValue(this.sections[0]);
    controls['section'].setValue(null);
    controls['win_login_name'].setValue('');
    controls['notes_mail'].setValue('');
    controls['post_title'].setValue('');
    controls['surname'].setValue('');
    controls['givenname'].setValue('');
    controls['uam_id'].setValue('');
  }

  /////////////////////// For Pop Up //////
  can_show: boolean = false;
  header: string;

  onChildClose(event) {
    this.can_show = false;
  }

  onHide() {
    this.can_show = false;
  }

  onRowSelect(event) {
    //this.selectedRequest = event.data;
    let eventData = event.data;
    let id = eventData.id;
    let uam_id = eventData['uam_id'];
    this.data.getUser(id).subscribe(
      data => {
        this.header = 'Account Enquiry  ----  UAM ID  :  ' + uam_id + '(' + id + ')';
        let formData = data;;
        this.selectedItem = formData;
        this.can_show = true;
      }, error => {
        this.utils.promptError(error, 'Cannot get user information');
        console.log(error.message);
      }
    )
  }

  onRowUnselect(event) {
    this.selectedItem = null;
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


