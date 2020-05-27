import { Component, OnInit, Input, Output, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { GenericAccountRequest, UploadFile_Permission } from '../../models/models';
import { FormGroup, FormBuilder } from '@angular/forms';
import { CommunicationService } from '../../judCommon/communication.service';
import { BasicUserInfoComponent } from '../basic-user-info/basic-user-info.component';
import { FormatDatePipe } from '../../judCommon/formatDate.pipe';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { FileMaintainerComponent } from '../file-maintainer/file-maintainer.component';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-requests-detail-account-new',
  templateUrl: './requests-detail-account-new.component.html',
  styleUrls: ['./requests-detail-account-new.component.css'],
})

export class RequestsDetailNewAccountComponent implements OnInit {

  @ViewChild('reqFileMaintainer', { static: true }) reqFileMaintainer: FileMaintainerComponent;
  @ViewChild('file_btn', { static: false }) file_btn: ElementRef;
  @ViewChild('basicUserInfo', { static: false }) basicUserInfo: BasicUserInfoComponent;
  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;
  @ViewChild('autoCompleteObject', { static: true }) autoCompleteObject: any;
  @Output() closeEvent = new EventEmitter<boolean>();
  @Input() set request(val: GenericAccountRequest) {
    this._request = val;
    if (!("uploaded_files" in this._request)) {
      this._request["uploaded_files"] = {};
    }
    this._patchValueFromRequestToForm();
  }

  _request: GenericAccountRequest;
  canEdit: boolean = false;
  localForm: FormGroup;
  suggestedEmails: any[];
  selecedFiles: any[] = [];
  isShowContactInfo: boolean;
  status: any;
  resType: any;
  createDate: Date;
  modifyDate: Date;
  creation_user: string;
  last_modification_user: string;
  reqStatus: string;

  uploadfile_permissions: UploadFile_Permission[] = [
    { status: 0, description: 'From Requester', canEdit: true }
  ]
  get request(): GenericAccountRequest {
    return this._request;
  }

  constructor(private data: DataService, private comm: CommunicationService, private utils: UtilService,
    private _fb: FormBuilder) { }

  ngOnInit() {
    this.localForm = this._fb.group({
      oth_other_request: [''],
      review_by: [''],
      copy_to: [''],
      attachment: [null],
    });
    this.status = this._request['status'];
    this.resType = this._request['resourcetype'];
    this.canEdit = (this.status == 0) && (this.resType == 'CreateAccountRequest' || this.resType == 'UpdateAccountRequest') && (!this._request.read_only);
    this.isShowContactInfo = (this.resType == 'CreateAccountRequest');

    this.createDate = this.request['creation_date'];
    this.modifyDate = this.request['last_modification_date'];
    this.creation_user = this.request.creation_user;
    this.last_modification_user = this.request.last_modification_user;
    this.reqStatus = this.request['request_status_name'];
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      let header = '';
      if (this.status == 0 && this.resType == 'CreateAccountRequest') {
        header = 'Request New Account';
      } else if (this.status == 0 && this.resType == 'UpdateAccountRequest') {
        header = 'Request Upate Account';
      } else {
        header = 'View Completed/Rejected Request';
      }
      this.comm.setHeader(header);
      this._patchValueFromRequestToForm();
      //this.comm.setHeader(this._request.status == 0 ? 'Request New Account' : 'View Completed/Rejected Request');        
    });
    setTimeout(() => {
      this.autoCompleteObject.focusInput();
    }, 500);
  }

  toggleEditMode() {
    this.canEdit = !this.canEdit;
    // this.changeEditMode.emit(this.canEdit);
  }

  canHandle(): boolean {
    // return (this._request.status == 0);
    return (this._request.status == 0) && !this._request.read_only;
  }

  private _patchValueFromRequestToForm() {
    if (this.localForm && this._request) {
      if (this._request['mail_to']) {
        this._request['review_by'] = JSON.parse(JSON.stringify(this._request['mail_to'].to));
        this._request['copy_to'] = JSON.parse(JSON.stringify(this._request['mail_to'].cc));
      }
      for (let controlName in this.localForm.controls) {
        if (this.localForm.controls[controlName] instanceof FormGroup) {
          this.localForm.controls[controlName].patchValue(this._request);
          if (controlName == 'basic_user_infoForm') {
            let basicForm = this.localForm.controls[controlName] as FormGroup;
            //console.log(basicForm.controls);
            if (this._request) {
              basicForm.controls['title'].patchValue(this.basicUserInfo.titles.find(x => x.id == this._request['title']));  //titles
              // basicForm.controls['rank'].patchValue(this.basicUserInfo.ranks.find(x => x.id == this._request['rank']));  //ranks
              this.basicUserInfo.rank = this._request['master_rank'];
              // basicForm.controls['substantive_rank'].patchValue(this.basicUserInfo.sub_ranks.find(x => x.id == this._request['substantive_rank'])); //sub_ranks
              this.basicUserInfo.substantive_rank = this._request['substantive_rank'];
              basicForm.controls['account_type'].patchValue(this.basicUserInfo.acc_types.find(x => x.id == this._request['account_type'])); //acc_types
              // basicForm.controls['section'].patchValue(this.basicUserInfo.sections.find(x => x.id == this._request['section']));  //sections
              this.basicUserInfo.section = this._request['section'];
              basicForm.controls['account_effective_start_date'].patchValue(new FormatDatePipe().transform(this._request['account_effective_start_date']));  //account_effective_start_date
              basicForm.controls['account_effective_end_date'].patchValue(new FormatDatePipe().transform(this._request['account_effective_end_date']));  //account_effective_end_date
            }
          }
        } else {
          // if (controlName == 'review_by') {
          //   console.log(this._request['mail_to'].to);
          //   // this.localForm.controls[controlName].setValue(this._request['mail_to'].to);
          //   // this.localForm.controls['review_by'].setValue(['test', 'test2']);
          //   console.log(this.localForm.controls[controlName].value);
          //   console.log(this.localForm.controls[controlName]);
          // } if (controlName == 'copy_to') {
          //   // console.log(this._request['mail_to'].cc);
          //   // console.log(this.localForm.controls[controlName])
          //   // this.localForm.controls['copy_to'].setValue(this._request['mail_to'].cc);
          //   // console.log(this.localForm.controls[controlName].value);
          // } else {
          this.localForm.controls[controlName].patchValue(this._request[controlName]);
          // }
        }
      }
    }
  }

  private _patchValueFromFormToRequest() {
    // Object.assign(this._request, this.localForm.value);
    for (let controlName in this.localForm.controls) {
      // if (this.localForm.controls[controlName] instanceof FormGroup) {
      //   // console.log(this.localForm.controls[controlName].value);
      //   Object.assign(this._request, this.localForm.controls[controlName].value);
      // } else {
      //   this._request[controlName] = this.localForm.controls[controlName].value;
      // }
      this.utils.cloneFormToFlatObject(this._request, this.localForm.controls[controlName], controlName);
    }

    // ["title", "substantive_rank", "account_type",
    ["title", "account_type",
    ].forEach(element => {
      if (this._request[element] && this._request[element]["id"]) {
        this._request[element] = this._request[element]["id"];
      }
    });

    // if (this._request['section'] && "code" in this._request['section']) {
    //   this._request["section"] = this._request["section"]["code"];
    // }

    ["attachment",
    ].forEach(element => {
      delete this._request[element];
    });

    if (this._request.mail_to) {
      this._request.update_mail_to = JSON.parse(JSON.stringify(this._request.mail_to));
    }
    if (!('update_mail_to' in this._request)) {
      this._request.update_mail_to = { 'to': [], 'cc': [] }
    }
    if (this._request["review_by"]) {
      this._request.update_mail_to['to'] = this._request['review_by']
    }
    if (this._request["copy_to"]) {
      this._request.update_mail_to['cc'] = this._request['copy_to']
    }

    // let upfiles: any[] = [];
    // if (this.selecedFiles.length > 0) {
    //   this.selecedFiles.forEach(element => {
    //     let file = element as File;
    //     let data = { 'name': file.name, 'minetype': file.type };
    //     upfiles.push(data);
    //   }
    //   )
    //   this._request["files"] = upfiles;
    // }
    if (this._request.ad_user_groups) {
      this._request.update_ad_user_groups = this._request.ad_user_groups;
    }
    if (this._request.ad_user_groups) {
      this._request.update_ln_user_groups = this._request.ln_user_groups;
    }
  }

  onReset() {
    this.selecedFiles = [];
    this.localForm.reset();
    this._patchValueFromRequestToForm();
    this.reqFileMaintainer.clearUpload();
    // this.toggleEditMode();
  }

  onCancel() {
    // this._patchValueFromRequestToForm();
    // this.toggleEditMode();
    this.closeEvent.emit(true);
  }

  onSaveDraft() {
    // Object.assign(this._request, this.localForm.value);
    this.judDialog.showDialog('Information', 'The request is saving', 'wait', 'wait');
    this._patchValueFromFormToRequest();
    setTimeout(() => {
      let dataService = null;
      if (this.resType == 'CreateAccountRequest') {
        dataService = this.data.updateCreateAccountPrepare(this._request);
      } else {
        dataService = this.data.saveUpdateAccountPrepare(this._request);
      }
      dataService.subscribe(
        data => {
          this._request = data;
          this.reqFileMaintainer.uploadFiles(this._request.id);
          this.judDialog.showDialog('Information', `The request ${this._request.request_id} was saved successfully`, 'succ', 'info');
          this.comm.completed(this._request);
          this.toggleEditMode();
        },
        error => {
          // this.judDialog.showDialog('Save Draft Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Save Draft Failed');
        }
      )
    }, 500);
  }

  // confirm(submit: boolean) {
  confirm() {
    this.judDialog.showDialog('Confirmation', 'Are you sure to submit the request?', 'confirm', 'confirmSub');
  }

  onWithdraw() {
    this.judDialog.showDialog('Confirmation', 'Are you sure to withdraw the request?', 'confirm', 'confirmRej');

  }
  onDialogClose() {
    this.closeEvent.emit(true);
  }

  onDialogSubmit() {
    // Object.assign(this._request, this.localForm.value);
    let tmp_status: number = this._request.status;
    this.judDialog.showDialog('Information', 'The request is submitting', 'wait', 'wait');
    this._patchValueFromFormToRequest();
    setTimeout(() => {
      let dataService = null;
      if (this.resType == 'CreateAccountRequest') {
        dataService = this.data.submitCreateAccountPrepare(this._request);
      } else {
        dataService = this.data.submitUpdateAccountPrepare(this._request);
      }
      dataService.subscribe(
        data => {
          this._request = data;
          this.reqFileMaintainer.uploadFiles(this._request.id, tmp_status);
          this.judDialog.showDialog('Information', `The request ${this._request.request_id} was submitted successfully`, 'succ', 'info');
          this.comm.completed(this._request);
          this.toggleEditMode();
        },
        error => {
          // this.judDialog.showDialog('Submit Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Submit failed');
        }
      )
    }, 500);
  }

  onDialogWithdraw() {
    // Object.assign(this._request, this.localForm.value);
    let tmp_status: number = this._request.status;
    this.judDialog.showDialog('Information', 'Withdrawing the request', 'wait', 'wait');
    this._patchValueFromFormToRequest();
    setTimeout(() => {
      let dataService = null;
      if (this.resType == 'CreateAccountRequest') {
        dataService = this.data.withdrawCreateAccountPrepare(this._request);
      } else {
        dataService = this.data.withdrawUpdateAccountPrepare(this._request);
      }
      dataService.subscribe(
        data => {
          this._request = data;
          this.reqFileMaintainer.uploadFiles(this._request.id, tmp_status);
          this.judDialog.showDialog('Information', `The request ${this._request.request_id} was withdrawn successfully`, 'succ', 'info');
          this.comm.completed(this._request);
          this.toggleEditMode();
        },
        error => {
          // this.judDialog.showDialog('Withdrawal Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Withdraw failed');
        }
      )
    }, 500);
  }
  searchMail(event) {
    let query = event.query;
    let entered: string = event.query;
    // this.suggestedEmails = this.data.searchMail(entered);
    this.data.searchMail(entered).subscribe(
      data => {
        this.suggestedEmails = [];
        data.forEach((currentValue, idx, arr) => {
          this.suggestedEmails.push(currentValue['email']);
        })
      }, error => {
        this.utils.promptError(error, 'Cannot search mail');
        this.suggestedEmails = [];
      }
    )
  }

  onDeleteFile(deleted_files: number[]) {
    this._request.delete_files = deleted_files;
  }

  onUploadScreenUpdate(updated: boolean) {
    this.localForm.markAsDirty();
  }
}

