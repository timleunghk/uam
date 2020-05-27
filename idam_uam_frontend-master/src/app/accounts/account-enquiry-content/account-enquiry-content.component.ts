import { Component, OnInit, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { FormGroup, FormBuilder } from '@angular/forms';
import { BasicUserInfoComponent } from '../../requests/basic-user-info/basic-user-info.component';
import { UserInfoSystemsComponent } from '../../requests/user-info-systems/user-info-systems.component';
import { FormatDatePipe } from '../../judCommon/formatDate.pipe';

@Component({
  selector: 'app-account-enquiry-content',
  templateUrl: './account-enquiry-content.component.html',
  styleUrls: ['./account-enquiry-content.component.css'],
})

export class AccountEnquiryContentComponent implements OnInit {

  @ViewChild('basicUserInfo', { static: false }) basicUserInfo: BasicUserInfoComponent;
  @ViewChild('userInfoSys', { static: false }) userInfoSys: UserInfoSystemsComponent;
  @Output() closeEvent = new EventEmitter<boolean>();
  @Input() set item(val: any) {
    this.setData(val);
    this.can_show = true;
    this.creation_date = val.creation_date;
    this.last_modification_date = val.last_modification_date;
    this.creation_user = val.creation_user;
    this.last_modification_user = val.last_modification_user;
    this.account_status_name = val.account_status_name;
  }

  can_show: boolean = false;
  creation_date: string;
  last_modification_date: string;
  creation_user: string;
  last_modification_user: string;
  account_status_name: string;
  canEdit: boolean = false;
  localForm: FormGroup;
  selecedFiles: any[] = [];


  constructor(private _fb: FormBuilder) { 
    
  }

  ngOnInit() {
    this.localForm = this._fb.group({
      oth_other_user: [''],
      oth_other_justification: [''],
      oth_other_remark: [''],
      attachment: [null],
    });
  }

  ngAfterViewInit() {

  }

  setData(itemData: any): void {
    setTimeout(() => {
      if (this.localForm && itemData) {
        for (let controlName in this.localForm.controls) {
          if (this.localForm.controls[controlName] instanceof FormGroup) {
            this.localForm.controls[controlName].patchValue(itemData);
            if (controlName == 'basic_user_infoForm') {
              let basicForm = this.localForm.controls[controlName] as FormGroup;
              if (itemData) {
                basicForm.controls['title'].patchValue(this.basicUserInfo.titles.find(x => x.id == itemData['title']));  //titles
                // basicForm.controls['rank'].patchValue(this.basicUserInfo.ranks.find(x => x.id == itemData['rank']));  //ranks
                // basicForm.controls['substantive_rank'].patchValue(this.basicUserInfo.sub_ranks.find(x => x.id == itemData['substantive_rank'])); //sub_ranks
                this.basicUserInfo.rank = itemData['master_rank'];
                this.basicUserInfo.substantive_rank = itemData['substantive_rank'];
                basicForm.controls['account_type'].patchValue(this.basicUserInfo.acc_types.find(x => x.id == itemData['account_type'])); //acc_types
                // basicForm.controls['section'].patchValue(this.basicUserInfo.sections.find(x => x.id == itemData['section']));  //sections
                this.basicUserInfo.section = itemData['section'];
                basicForm.controls['account_effective_start_date'].patchValue(new FormatDatePipe().transform(itemData['account_effective_start_date']));  //account_effective_start_date
                basicForm.controls['account_effective_end_date'].patchValue(new FormatDatePipe().transform(itemData['account_effective_end_date']));  //account_effective_end_date
              }
            } else if (controlName == 'user_info_systemsForm') {
              let userInfoSystemsForm = this.localForm.controls[controlName] as FormGroup;
            }
          } else {
            this.localForm.controls[controlName].patchValue(itemData[controlName]);
          }
        }
        if (itemData.ad_user_groups) {
          this.userInfoSys.selected_adgroup = itemData.ad_user_groups;
        }
        if (itemData.ln_user_groups) {
          this.userInfoSys.selected_lngroup = itemData.ln_user_groups;
        }
        if (itemData['ad_ps_magistrate_of_lt']) {
          this.userInfoSys.ad_ps_magistrate_of_lt = itemData.ad_ps_magistrate_of_lt;
        }
      }
    });
  }

  onClose() {
    this.closeEvent.emit(true);
  }

  doViewFile(selectedFile) {

  }


}
