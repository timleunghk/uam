import { Component, OnInit, Input, Output, EventEmitter, ChangeDetectorRef, ViewChild, ElementRef } from '@angular/core';
import { GenericAccountReview, UploadFile_Permission } from '../../models/models';
import { FormGroup, FormBuilder } from '@angular/forms';
import { DataService } from '../../judCommon/data.service';
import { CommunicationService } from '../../judCommon/communication.service';
import { BasicUserInfoComponent } from '../basic-user-info/basic-user-info.component';
import { UserInfoSystemsComponent } from '../user-info-systems/user-info-systems.component';
import { FormatDatePipe } from '../../judCommon/formatDate.pipe';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { FileMaintainerComponent } from '../file-maintainer/file-maintainer.component';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-requests-detail-account-review',
  templateUrl: './requests-detail-account-review.component.html',
  styleUrls: ['./requests-detail-account-review.component.css'],
})

export class RequestsDetailNewAccountReviewComponent implements OnInit {

  @ViewChild('reqFileMaintainer', { static: true }) reqFileMaintainer: FileMaintainerComponent;
  uploadfile_permissions: UploadFile_Permission[] = [
    { status: 0, description: 'From Requester', canEdit: false },
    { status: 1, description: 'From ITOO Reviewer', canEdit: true }
  ]
  @ViewChild('file_btn', { static: false }) file_btn: ElementRef;
  @ViewChild('basicUserInfo', { static: false }) basicUserInfo: BasicUserInfoComponent;
  @ViewChild('userInfoSys', { static: false }) userInfoSys: UserInfoSystemsComponent;
  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;
  @ViewChild('autoCompleteObject', { static: true }) autoCompleteObject: any;
  @Output() closeEvent = new EventEmitter<boolean>();
  @Input() set request(val: GenericAccountReview) {
    this._request = val;
    this._patchValueFromRequestToForm();
  }

  _request: GenericAccountReview;
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
  submitDate: Date;

  get request(): GenericAccountReview {
    return this._request;
  }

  constructor(private data: DataService, private comm: CommunicationService, private _fb: FormBuilder, private utils: UtilService,
    private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    this.localForm = this._fb.group({
      oth_other_request: [''],
      oth_other_justification: [''],
      review_by: [''],
      copy_to: [''],
      attachment: [null],
    });
    this.status = this._request['status'];
    this.resType = this._request['resourcetype'];
    // this.canEdit = (this.status == 1) && (this.resType == 'CreateAccountRequest' || this.resType == 'UpdateAccountRequest');
    this.canEdit = (this.status == 1) && (this.resType == 'CreateAccountRequest' || this.resType == 'UpdateAccountRequest') && (!this._request.read_only);
    this.isShowContactInfo = (this.resType == 'CreateAccountRequest');

    this.createDate = this.request['creation_date'];
    this.modifyDate = this.request['last_modification_date'];
    this.creation_user = this.request.creation_user;
    this.last_modification_user = this.request.last_modification_user;
    this.reqStatus = this.request['request_status_name'];
    this.submitDate = this.request['submission_date'];
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      let header = '';
      if (this.status == 1 && this.resType == 'CreateAccountRequest') {
        header = 'Review New Account';
      } else if (this.status == 1 && this.resType == 'UpdateAccountRequest') {
        header = 'Review Upate Account';
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
    this.cdr.detectChanges();
  }

  canHandle(): boolean {
    // return (this._request.status == 1);
    return (this._request.status == 1) && !this._request.read_only;
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
            if (this._request) {
              basicForm.controls['title'].patchValue(this.basicUserInfo.titles.find(x => x.id == this._request['title']));  //titles
              // basicForm.controls['rank'].patchValue(this.basicUserInfo.ranks.find(x => x.id == this._request['rank']));  //ranks
              this.basicUserInfo.rank = this._request['master_rank'];
              this.basicUserInfo.substantive_rank = this._request['substantive_rank'];
              // basicForm.controls['substantive_rank'].patchValue(this.basicUserInfo.sub_ranks.find(x => x.id == this._request['substantive_rank'])); //sub_ranks
              basicForm.controls['account_type'].patchValue(this.basicUserInfo.acc_types.find(x => x.id == this._request['account_type'])); //acc_types
              // basicForm.controls['section'].patchValue(this.basicUserInfo.sections.find(x => x.id == this._request['section']));  //sections
              this.basicUserInfo.section = this._request['section'];
              basicForm.controls['account_effective_start_date'].patchValue(new FormatDatePipe().transform(this._request['account_effective_start_date']));  //account_effective_start_date
              basicForm.controls['account_effective_end_date'].patchValue(new FormatDatePipe().transform(this._request['account_effective_end_date']));  //account_effective_end_date
            }
          } else if (controlName == 'user_info_systemsForm') {
            let userInfoSystemsForm = this.localForm.controls[controlName] as FormGroup;
            if (this._request.ad_user_groups) {
              this.userInfoSys.selected_adgroup = this._request.ad_user_groups;
            }
            if (this._request.ln_user_groups) {
              this.userInfoSys.selected_lngroup = this._request.ln_user_groups;
            }
            if (this._request.ad_account_expiry_date) {
              this.userInfoSys.ad_account_expiry_date = this._request.ad_account_expiry_date;
            }
            if (this._request.ad_ps_magistrate_of_lt) {
              this.userInfoSys.ad_ps_magistrate_of_lt = this._request.ad_ps_magistrate_of_lt;
            }
          }
        } else {
          this.localForm.controls[controlName].patchValue(this._request[controlName]);
        }
      }
    }
  }

  private _patchValueFromFormToRequest() {
    for (let controlName in this.localForm.controls) {
      this.utils.cloneFormToFlatObject(this._request, this.localForm.controls[controlName], controlName);
      // if (this.localForm.controls[controlName] instanceof FormGroup) {
      //   console.log(this.localForm.controls[controlName].getRawValue());
      //   // Object.assign(this._request, this.localForm.controls[controlName].value);
      //   this.utils.cloneObject(this._request, this.localForm.controls[controlName].value);
      //   // for (let field in this.localForm.controls[controlName]['controls']) {
      //   //   if (field['disabled']) {
      //   //     console.log(field);
      //   //   }

      //   // }
      // } else {
      //   this._request[controlName] = this.localForm.controls[controlName].value;
      // }
    }
    console.log(this._request);
    // alert(this._request['ln_database_quota']);
    // ["title", "rank", "substantive_rank", "account_type",
    ["title", "account_type",
      // , "ad_location", "ln_mps_range", "ln_internet_mail_user", "ln_inotes_user"
      // , "ln_gcn_user", "ln_contractor", "ln_con_mail_user", "ln_mail_system", "ln_mail_server", "ln_mail_file_owner_access"
      // , "ln_mail_file_template", "ln_mail_domain", "ln_license_type"
      // , "dp_rank_code", "dp_staff_code", "dp_emp_type", "jjo_mail_domain"
    ].forEach(element => {
      if (this._request[element] && this._request[element]["id"]) {
        this._request[element] = this._request[element]["id"];
      }
    });

    // if (this._request['section'] && "code" in this._request['section']) {
    //   this._request["section"] = this._request["section"]["code"];
    // }

    // ["ln_grp_filter", "ad_grp_filter", "ad_windows_ass_group", "ln_ass_group", "attachment",
    ["ad_windows_ass_group", "ln_ass_group",
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

    this._request.ad_ps_magistrate_of_lt = this.userInfoSys.ad_ps_magistrate_of_lt;

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

    if (this.userInfoSys.ad_windows_ava_groups) {
      this._request.update_ad_user_groups = this.userInfoSys.ad_windows_ava_groups;
    }
    if (this.userInfoSys.ln_ava_groups) {
      this._request.update_ln_user_groups = this.userInfoSys.ln_ava_groups;
    }

  }

  onReset() {
    // this.toggleEditMode();
    this.localForm.reset();
    this._patchValueFromRequestToForm();
    this.reqFileMaintainer.clearUpload();
  }

  onCancel() {
    // this._patchValueFromRequestToForm();
    // this.toggleEditMode();
    this.closeEvent.emit(true);
  }

  onSaveDraft() {
    this.judDialog.showDialog('Information', 'The draft of reviewing request is saving', "wait", 'wait');
    this._patchValueFromFormToRequest();
    setTimeout(() => {
      let dataService = null;
      if (this.resType == 'CreateAccountRequest') {
        dataService = this.data.updateCreateAccountReview(this._request);
      } else {
        dataService = this.data.saveUpdateAccountReview(this._request);
      }
      //this.data.updateCreateAccountReview(this._request).subscribe(
      dataService.subscribe(
        data => {
          this._request = data;
          this.reqFileMaintainer.uploadFiles(this._request.id);
          this.judDialog.showDialog('Information', 'The draft of reviewing request was saved successfully', 'succ', 'info');
          this.comm.completed(this._request);
          this.toggleEditMode();
        },
        error => {
          // this.judDialog.showDialog('Save Draft Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Save Draft failed');
        }
      )
    }, 500);
  }

  onDialogClose() {
    this.closeEvent.emit(true);
  }

  onSubmit() {
    this.judDialog.showDialog('Information', 'Are you sure to submit the current request?', 'confirm', 'confirmSub');
  }

  onDialogSubmit() {
    this.judDialog.showDialog('Information', 'The request is endorsing', 'wait', 'wait');
    let tmp_status: number = this._request.status;
    this._patchValueFromFormToRequest();
    setTimeout(() => {
      let dataService = null;
      if (this.resType == 'CreateAccountRequest') {
        dataService = this.data.endorseCreateAccountReview(this._request);
      } else {
        dataService = this.data.endorseUpdateAccountReview(this._request);
      }
      //this.data.endorseCreateAccountReview(this._request).subscribe(
      dataService.subscribe(
        data => {
          this._request = data;
          this.reqFileMaintainer.uploadFiles(this._request.id, tmp_status);
          this.judDialog.showDialog('Information', 'The request was endorsed successfully', 'succ', 'info');
          this.comm.completed(this._request);
          this.toggleEditMode();
        },
        error => {
          // this.judDialog.showDialog('Confirmation Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Confirmation failed');
        }
      )
    }, 500);
  }

  canReject() {
    const value = this.localForm.controls['oth_other_justification'] ? this.localForm.controls['oth_other_justification'].value : null;
    return value != null && value.replace(/^\s+|\s+$/gm, '').length > 0;
  }

  onReject() {
    this.judDialog.showDialog('Information', 'Are you sure to reject the current request?', 'confirm', 'confirmRej');
  }

  onDialogReject() {
    this.judDialog.showDialog('Information', 'The request is rejecting by the reviewer', 'wait', 'wait');
    let tmp_status: number = this._request.status;
    this._patchValueFromFormToRequest();
    setTimeout(() => {
      let dataService = null;
      if (this.resType == 'CreateAccountRequest') {
        dataService = this.data.rejectCreateAccountReview(this._request);
      } else {
        dataService = this.data.rejectUpdateAccountReview(this._request);
      }
      dataService.subscribe(
        //this.data.rejectCreateAccountReview(this._request).subscribe(
        data => {
          this._request = data;
          this.reqFileMaintainer.uploadFiles(this._request.id, tmp_status);
          this.judDialog.showDialog('Information', 'The request was rejected by the reviewer successfully', 'succ', 'info');
          this.comm.completed(this._request);
          this.toggleEditMode();
        },
        error => {
          // this.judDialog.showDialog('Reject Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Reject failed');
        }
      )
    });
  }

  searchMail(event: any) {
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
