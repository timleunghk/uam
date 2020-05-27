import { Component, OnInit, ViewChild } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { BaseRequest, Section } from '../../models/models';
import { CommunicationService } from '../../judCommon/communication.service';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Table } from 'primeng/table';
import { ActivatedRoute } from '@angular/router';
import { LazyLoadEvent } from 'primeng/primeng';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-requests-list',
  templateUrl: './requests-list.component.html',
  styleUrls: ['./requests-list.component.css'],
  providers: [CommunicationService],
})

export class RequestsListComponent implements OnInit {

  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;
  @ViewChild('dt', { static: true }) userTable: Table;
  @ViewChild('request_id', { static: true }) request_id: any;
  selectedRequest: BaseRequest;
  // display: boolean = false;
  searchForm: FormGroup;

  totalRecords: number;
  tableItems: any[];
  loading: boolean;
  allowLazyLoad: boolean = false;
  defaultSortField: string = 'request_id';

  account_types: any[] = [{ id: '', value: 'ALL' }, { id: 1, value: 'JJO' }, { id: 2, value: 'Non-JJO' }, { id: 3, value: 'Special Account' }];
  // sections: any[] = [{ id: '', value: 'ALL' }, { id: 1, value: 'ITOO' }, { id: 2, value: 'ITOT' }, { id: 3, value: 'Finance' }];
  request_statuss: any[] = [
    { id: '', value: 'ALL' }
    , { id: 3, value: 'Confirmed By HelpDesk' }
    , { id: 9, value: 'Disable Account Completed' }
    , { id: 11, value: 'Delete Account Completed' }
    , { id: 10, value: 'Enable Account Completed' }
    , { id: 0, value: 'New Request' }
    , { id: 1, value: 'Pending For ITOO\'s review' }
    , { id: 2, value: 'Pending For ITOT\'s review' }
    , { id: 8, value: 'Reset Password Completed' }
    , { id: 4, value: 'Rejected by ITOO' }
    , { id: 5, value: 'Rejected by ITOT' }
    , { id: 6, value: 'Setup Completed' }
    , { id: 12, value: 'Update Account Completed' }
    , { id: 7, value: 'User Acknowledge' }
    , { id: 13, value: 'Withdrawn' }
  ];

  request_types: any[] = [
    { id: '', value: 'ALL' }
    , { id: 'CreateAccount', value: 'Create Account' }
    // , { id: '4', value: 'Change Password' }   
    , { id: 'DeleteAccount', value: 'Delete Account' }
    , { id: 'DisableAccount', value: 'Disable Account' }
    , { id: 'ReenableAccount', value: 'Re-enable Account' }
    , { id: 'ResetPassword', value: 'Reset Password' }
    , { id: 'UpdateAccount', value: 'Update Account' }

  ];

  constructor(public data: DataService, private comm: CommunicationService, private _fb: FormBuilder, private utils: UtilService, private route: ActivatedRoute) {
    comm.objCompleted$.subscribe(
      data => Object.assign(this.selectedRequest, data)
    );
  }

  ngOnInit() {
    this.loading = true;
    this.userTable.first = 0;
    this.userTable.sortField = this.defaultSortField;
    this.userTable.sortOrder = 1;
    this.searchMain(1, 1, null, 1);

    this.searchForm = this._fb.group({
      request_id: [''],
      request_by: [''],
      request_status: [''],
      request_type: [''],
      surname: [''],
      given_name: [''],
      section: [''],
      account_type: [''],
    });

    setTimeout(() => {
      this.onReset();
    }, 500);
    this.request_id.nativeElement.focus();
  }

  loadTableLazy(event: LazyLoadEvent) {
    if (this.allowLazyLoad) {
      this.loading = true;
      let page = event.first / event.rows + 1;
      this.searchMain(0, page, event.sortField, event.sortOrder);
    }
  }

  onSearch() {
    // To avoid auto trigger of lazyload, which result in simultaneous multiple requests to backend server
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
      searchObject['request_id'] = this.searchForm.value['request_id'];
      searchObject['request_by'] = this.searchForm.value['request_by'];
      searchObject['request_status'] = this.searchForm.value['request_status'].id;
      searchObject['request_type'] = this.searchForm.value['request_type'].id;
      searchObject['surname'] = this.searchForm.value['surname'];
      searchObject['given_name'] = this.searchForm.value['given_name'];
      searchObject['section'] = (this.searchForm.value['section'] === null) ? null : this.searchForm.value['section'].code;
      searchObject['account_type'] = this.searchForm.value['account_type'].id;
    }
    searchObject['rows'] = this.userTable.rows;
    searchObject['page'] = page;
    // searchObject['sortField'] = sortField;
    // searchObject['sortOrder'] = sortOrder;
    if (sortField) {
      searchObject['ordering'] = ((sortOrder < 0) ? '-' : '') + sortField;
    }
    this.data.getAllRequests(searchObject).subscribe(
      data => {
        this.tableItems = data['results'];
        this.totalRecords = data['count'];
        this.loading = false;
        this.allowLazyLoad = true;
      },
      error => {
        // this.judDialog.showDialog('Search Error', this.utils.parseError(error), 'error', 'info');
        this.utils.promptError(error,' Search Failed');
        this.loading = false;
      }
    )

    /*
      let data = await this.data.getAllRequestsAsync(searchObject);
      this.tableItems = data['results'];
      this.totalRecords = data['count'];
      this.loading = false;
      this.allowLazyLoad = true;	
    */

  }

  onReset() {
    this.userTable.first = 0;
    //this.first = 0;
    //this.searchForm.reset();
    let controls = this.searchForm.controls;
    controls['request_id'].setValue('');
    controls['request_by'].setValue('');
    controls['request_status'].setValue(this.request_statuss[0]);
    controls['request_type'].setValue(this.request_types[0]);
    controls['surname'].setValue('');
    controls['given_name'].setValue('');
    // controls['section'].setValue(this.sections[0]);
    controls['section'].setValue(null);
    controls['account_type'].setValue(this.account_types[0]);
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      let sId = this.route.snapshot.queryParamMap.get('id');
      if (sId != null) {
        if (Number(sId)) {
          this.selectedRequest = { 'id': Number(sId), 'resourcetype': 'CreateAccountRequest', 'status': 0 } as BaseRequest;
        } else {
          this.judDialog.showDialog('Error', 'Open Failed : ' + 'The link is invalid', 'error', 'info');
        }
      }
    }, 500);
  }

  onRowSelect(event) {
    this.selectedRequest = event.data;
    //console.log(event.data)
    //this.router.navigate(['requests', event.data['id'], 'create-account-detail']);
    //this.display = true;
  }

  onRowUnselect(event) {
    this.selectedRequest = null;
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
        console.log(error);
      }
    )
  }

}
