import { Component, OnInit, Input, EventEmitter, Output, ViewContainerRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ValidatorFn, FormControl } from '@angular/forms';
import { CommunicationService } from '../../judCommon/communication.service';
import { DataService } from '../../judCommon/data.service';
import { AdGroup, LnGroup, GenericAccountRequest } from '../../models/models';
import { UtilService } from '../../judCommon/util.service';
import { FormatDatePipe } from '../../judCommon/formatDate.pipe';
import { SelectItem } from 'primeng/api';

@Component({
  selector: 'app-user-info-systems',
  templateUrl: './user-info-systems.component.html',
  styleUrls: ['./user-info-systems.component.css']
})
export class UserInfoSystemsComponent implements OnInit {

  @Input() parentForm: FormGroup;
  @Input() groupName: string;
  @Input() canEdit: boolean = false;
  @Output() winNameEvent = new EventEmitter<string>();
  @Output() notesNameEvent = new EventEmitter<string>();
  @Input() request: GenericAccountRequest;
  no_roma_found = false;
  roma_loading = false;

  private _original_ad_windows_user_groups: AdGroup[] = [];
  // private _original_ad_windows_ava_groups: AdGroup[] = []
  @Input() set selected_adgroup(adgroups: AdGroup[]) {
    // this._original_ad_windows_ava_groups = adgroups;
    this.ad_windows_ava_groups = JSON.parse(JSON.stringify(adgroups));
    let tmp_groups: AdGroup[] = []
    this._original_ad_windows_user_groups.forEach(
      element => {
        let ad_user_group = adgroups.find(x => x.id == element.id);
        if (ad_user_group) {

        } else {
          tmp_groups.push(element)
        }
      }
    )
    this.ad_windows_ass_groups = tmp_groups;
  }

  private _original_ln_groups: LnGroup[] = [];
  @Input() set selected_lngroup(lngroups: LnGroup[]) {
    this.ln_ava_groups = JSON.parse(JSON.stringify(lngroups));
    let tmp_groups: LnGroup[] = [];
    this._original_ln_groups.forEach(
      element => {
        let ln_group = lngroups.find(x => x.id == element.id);
        if (ln_group) {
        } else {
          tmp_groups.push(element);
        }
      }
    )
    this.ln_ass_groups = tmp_groups;
  }
  private tmp_ad_login_name: string;
  private _ad_account_expiry_date: Date;
  @Input() set ad_account_expiry_date(date: any) {
    if (date) {
      if (date instanceof Date) {
        this._ad_account_expiry_date = date;
        this.form.controls['ad_account_expiry_date'].patchValue(this._ad_account_expiry_date);
      } else if (typeof (date) === 'string') {
        this._ad_account_expiry_date = new FormatDatePipe().transform(date);
        this.form.controls['ad_account_expiry_date'].patchValue(this._ad_account_expiry_date);
      }
    }
  }

  private _ad_ps_magistrate_of_lt: string[];
  @Input() set ad_ps_magistrate_of_lt(instr: string[]) {
    if (instr) {
      this._ad_ps_magistrate_of_lt = instr;
      this.form.controls['ad_ps_magistrate_of_lt'].patchValue(this._ad_ps_magistrate_of_lt);
    }
  }

  get ad_ps_magistrate_of_lt(): string[] {
    this._ad_ps_magistrate_of_lt = this.form.controls['ad_ps_magistrate_of_lt'].value;
    return this._ad_ps_magistrate_of_lt;
  }
  formName: string;
  form: FormGroup;
  suggestedWindowsPS: any[];
  basicControls: any;
  password: string;

  // ad_locations: any[] = [
  //   { id: 'CN=Users', value: 'CN=Users' }, { id: 'OU=Marshall', value: 'OU=Marshall' }
  // ];
  ad_locations: SelectItem[] = [];

  ad_windows_ass_groups: AdGroup[] = [];

  ad_windows_ava_groups: AdGroup[] = [];


  ln_ass_groups: LnGroup[] = [];

  ln_ava_groups: LnGroup[] = [];

  boolean_choices: any[] = [
    { 'label': 'Yes', 'value': true },
    { 'label': 'No', 'value': false },
  ]
  jjo_mail_domains: SelectItem[] = [];

  jjo_emp_types: SelectItem[] = [];

  dp_rank_codes: SelectItem[] = [];


  dp_staff_codes: SelectItem[] = [];


  dp_emp_types: SelectItem[] = [];

  // ln_account_types: any[] = [
  //   { id: 1, value: 'R7.5' }, { id: 2, value: 'R7' }, { id: 3, value: 'R8' }
  // ];
  ln_account_types: SelectItem[] = [];


  ln_mps_ranges: SelectItem[] = [];


  // ln_client_licenses: any[] = [
  //   { id: 1, value: 'R7' }, { id: 2, value: 'R8' }, { id: 3, value: 'R9' }
  // ];
  ln_client_licenses: SelectItem[] = [];

  ln_mail_systems: SelectItem[] = [];

  ln_mail_servers: SelectItem[] = [];

  ln_mail_file_owner_accesss: SelectItem[] = [];

  ln_mail_file_templates: SelectItem[] = [];

  ln_mail_domains: SelectItem[] = [];

  ln_license_types: SelectItem[] = [];


  constructor(private _fb: FormBuilder, private comm: CommunicationService, private viewContainerRef: ViewContainerRef, private utils: UtilService, private data: DataService) {
    this.comm.userName$.subscribe(
      data => {
        let name = data.name.join(' ');
        this.tmp_ad_login_name = name;
        let ad_value = this.form.controls['ad_windows_login_name'].value;
        if ((!ad_value) || data.force_change) {
          //this.form.controls['ad_windows_login_name'].setValue(name);
        }
        let notes_value = this.form.controls['ln_lotus_notes_mail_name'].value;
        if ((!notes_value) || data.force_change) {
          // this.form.controls['ln_lotus_notes_mail_name'].setValue(name);
        }
      }
    );
  }

  private _validate_required_string(opt_field: string, fields: object): ValidatorFn {
    return (form: FormGroup): { [key: string]: any } | null => {
      const is_required_field = this.form.controls[opt_field];
      const toReturn = {};
      if (is_required_field.value) {
        // console.log(fields)
        for (let field in fields) {
          // console.log(field);
          const value = this.form.controls[field].value;
          let len = fields[field]['len'] ? fields[field]['len'] : 1;
          let errkey = fields[field]['errkey']
          if (value == null || value.replace(/^\s+|\s+$/gm, '').length < len) {
            toReturn[errkey] = true;
          }
        }
      }
      return Object.keys(toReturn).length > 0 ? toReturn : null;
    }
  }

  InternetMailValidator: ValidatorFn = (fg: FormGroup) => {
    let result = null;
    if (this.form.get('oa_need_lotus_notes').value) {
      if (this.form.get('ln_is_internet_mail_user').value && !this.form.get('ln_internet_address').value) {

        result = { valid: false };
      }
      this.form.get('ln_internet_address').setErrors(result);
    }
    return result;
  }
  private loadCodeTables() {
    // if (! this.canEdit) {
    //   return;
    // }
    this.data.getAdOuList().subscribe(
      data => {
        this.ad_locations = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ad_ou']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load AD OU list for selection');
      }
    );
    this.data.getLnAccTypes().subscribe(
      data => {
        this.ln_account_types = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_account_type']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Lotus Notes Account Type list');
      }
    );
    this.data.getLnClientLicenses().subscribe(
      data => {
        this.ln_client_licenses = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_client_license']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Lotus Notes Client Licenses list ');
      }
    );
    this.data.getLnMpsRanges().subscribe(
      data => {
        this.ln_mps_ranges = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_mps_range']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load MPS Range list ');
      }
    );
    this.data.getLnMailServers().subscribe(
      data => {
        this.ln_mail_servers = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_mail_server']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Mail Server list ');
      }
    );
    this.data.getLnMailFileOwners().subscribe(
      data => {
        this.ln_mail_file_owner_accesss = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_mail_file_owner']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load File Owner Access list ');
      }
    );
    this.data.getLnMailSystems().subscribe(
      data => {
        this.ln_mail_systems = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_mail_system']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Mail System list ');
      }
    );
    this.data.getLnMailTemplates().subscribe(
      data => {
        this.ln_mail_file_templates = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_mail_template']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Mail File Template list ');
      }
    );
    this.data.getLnLicenseTypes().subscribe(
      data => {
        this.ln_license_types = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_license_type']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load license type list ');
      }
    );
    this.data.getLnMailDomains().subscribe(
      data => {
        this.ln_mail_domains = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['ln_mail_domain']);
        this.jjo_mail_domains = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['jjo_mail_domain']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Internet Address Domain list ');
      }
    );
    this.data.getDpEmpTypes().subscribe(
      data => {
        this.dp_emp_types = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['dp_emp_type']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Internet Address Domain list ');
      }
    );
    this.data.getDpRankCodes().subscribe(
      data => {
        this.dp_rank_codes = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['dp_rank_code']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Internet Address Domain list ');
      }
    );
    this.data.getDpStaffCodes().subscribe(
      data => {
        this.dp_staff_codes = this.utils.convertSimpleCodeListToSelectItem(data, this.form.controls['dp_staff_code']);
      },
      error => {
        this.utils.promptError(error, 'Cannot load Internet Address Domain list ');
      }
    );

    this.data.getAdGroups().subscribe(
      data => {
        this._original_ad_windows_user_groups = data;
        let tmp_groups: AdGroup[] = [];
        this._original_ad_windows_user_groups.forEach(
          element => {
            let obj = this.ad_windows_ava_groups.find(x => x.id == element.id);
            if (obj) {
            } else {
              tmp_groups.push(element);
            }
          }
        )
        this.ad_windows_ass_groups = tmp_groups;
      },
      error => {
        this.utils.promptError(error, 'Cannot find AD Groups');
      }
    );
    this.data.getLnGroups().subscribe(
      data => {
        this._original_ln_groups = data;
        let tmp_groups: LnGroup[] = [];
        this._original_ln_groups.forEach(
          element => {
            let obj = this.ln_ava_groups.find(x => x.id == element.id);
            if (obj) {
            } else {
              tmp_groups.push(element);
            }
          }
        )
        this.ln_ass_groups = tmp_groups;
      },
      error => {
        this.utils.promptError(error, 'Cannot find LN Groups');
      }
    )

  }
  ngOnInit() {
    this.formName = `${this.groupName}Form`;
    this.form = this._fb.group({
      oa_need_windows_login: [false, [Validators.required]],
      ad_windows_login_name: [''],
      ad_windows_login_password: [''],
      ad_need_change_password_next_login: [''],
      ad_account_expiry_date: [null],
      ad_is_magistrate_of_lt: [false],
      ad_ps_magistrate_of_lt: [[]],
      // ad_windows_ass_group: [''],
      // ad_windows_ava_group: [''],
      // ad_grp_filter: [''],
      // ad_location: [''],
      ad_ou: [null],
      ad_windows_first_name: [''],
      ad_windows_last_name: [''],

      oa_need_lotus_notes: [false, [Validators.required]],
      ln_lotus_notes_mail_name: [''],
      ln_notes_password: [''],
      ln_first_name: [''],
      ln_last_name: [''],
      ln_middle_name: [''],
      ln_short_name: [''],
      ln_account_type: [null],
      ln_mps_range: [null],
      ln_client_license: [null],
      // ln_internet_mail_user: [''],
      ln_is_internet_mail_user: [false],
      ln_is_inote_user: [false],
      ln_is_gcn_user: [false],
      ln_is_contractor: [false],
      ln_is_confidential_mail_user: [false],
      ln_mail_system: [null],
      ln_mail_server: [null],
      ln_mail_file_name: [''],
      ln_mail_file_owner: [null],
      ln_mail_template: [null],
      ln_database_quota: [null],
      ln_warning_threshold: [null],
      ln_set_database_quota: [false],
      ln_set_warning_threshold: [false],
      ln_internet_address: [''],
      ln_mail_domain: [null],
      ln_license_type: [null],
      ln_remarks: [''],
      // ln_grp_filter: [''],
      // ln_ass_group: [''],
      // ln_ava_group: [''],

      oa_need_dp: [false, [Validators.required]],
      dp_login_id: [''],
      dp_dep_id: [''],
      dp_uid_saml: [''],
      dp_rank_code: [null],
      dp_staff_code: [null],
      dp_net_mail: [''],
      dp_first_name: [''],
      dp_last_name: [''],
      dp_emp_type: [null],
      dp_roma_id: [''],
      dp_roma_full_name: [''],
      dp_hkid: [''],

      oa_need_jjo: [false, [Validators.required]],
      jjo_login_id: [''],
      jjo_email: [''],
      jjo_first_name: [''],
      jjo_last_name: [''],
      jjo_mail_domain: [null],
      jjo_emp_type: [null],

    });
    this.form.setValidators(
      [
        this._validate_required_string('oa_need_windows_login', { 'ad_windows_login_name': { len: 3, errkey: 'ad_windows_login_name_empty' } }),
        this._validate_required_string('oa_need_windows_login', { 'ad_windows_login_password': { len: 3, errkey: 'ad_windows_pwd_empty' } }),
        this._validate_required_string('oa_need_lotus_notes', { 'ln_lotus_notes_mail_name': { len: 3, errkey: 'ln_lotus_notes_mail_name_empty' } }),
        this._validate_required_string('oa_need_lotus_notes', { 'ln_last_name': { len: 2, errkey: 'ln_lotus_notes_last_name_empty' } }),
        this._validate_required_string('oa_need_lotus_notes', { 'ln_middle_name': { len: 1, errkey: 'ln_lotus_notes_middle_name_empty' } }),
        this._validate_required_string('oa_need_lotus_notes', { 'ln_first_name': { len: 2, errkey: 'ln_lotus_notes_first_name_empty' } }),
        this._validate_required_string('oa_need_lotus_notes', { 'ln_notes_password': { len: 3, errkey: 'ln_lotus_notes_pwd_empty' } }),
        this._validate_required_string('oa_need_lotus_notes', { 'ln_short_name': { len: 1, errkey: 'ln_lotus_notes_short_name_empty' } }),
        this._validate_required_string('oa_need_dp', { 'dp_login_id': { len: 3, errkey: 'dp_login_name_empty' } }),
        this._validate_required_string('oa_need_jjo', { 'jjo_login_id': { len: 3, errkey: 'jjo_login_name_empty' } }),
        this.InternetMailValidator,
      ]);
    this.parentForm.addControl(this.formName, this.form);
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.basicControls = this.getBasicUserInfoControl();
      let sysControls = this.form.controls;
      let is_win = sysControls['oa_need_windows_login'].value;
      let is_notes = sysControls['oa_need_lotus_notes'].value;
      let is_dp = sysControls['oa_need_dp'].value;
      let is_jjo = sysControls['oa_need_jjo'].value;

      this.password = this.genRandString() + (Math.floor(Math.random() * (999999 - 111111 + 1)) + 111111) + this.genRandString();

      if (is_win) {
        this.setWinValues(true);
      }

      if (is_notes) {
        this.setNotesValues(true);
      }

      if (is_dp) {
        this.setDPValues(true);
      }

      if (is_jjo) {
        this.setJJOValues(true);
      }
      this.loadCodeTables();

    }, 500);
  }

  genRandString() {
    let text = "";
    let possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    for (var i = 0; i < 3; i++)
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
  }

  genLoginName(basicFirstName, basicSurname, basicPreName) {
    let givenNameArray = basicFirstName.split(' ');
    let givenNameString = "";

    for (let i = 0; i < givenNameArray.length; i++) {
      givenNameString += givenNameArray[i].substring(0, 1);
    }

    // let comLoginId = basicPreName + ' ' + givenNameString.toUpperCase() + ' '
    //   + basicSurname.substring(0, 1).toUpperCase() + basicSurname.substring(1).toLowerCase();
    let comLoginId = [this.utils.formatName(basicPreName), givenNameString.toUpperCase(), this.utils.formatName(basicSurname)].join(' ');
    return comLoginId;
  }

  canEditTab(field: string) {
    return this.canEdit ? this.form.controls[field].value : false;
  }

  canViewTab(field: string) {
    return this.form.controls[field].value;
  }

  searchWindowsPS(event) {
    let query = event.query;
    let entered: string = event.query;
    this.data.getPS(entered).subscribe(
      data => {
        this.suggestedWindowsPS = [];
        data.forEach((currentValue, idx, arr) => {
          this.suggestedWindowsPS.push(currentValue['ad_windows_login_name']);
        })
      },
      error => {
        this.utils.promptError(error, 'Cannot search PS names');
      }
    )
  }

  dp_get_roma_info() {
    this.roma_loading = true;
    let controls = this.form.controls;
    let roma_id = controls['dp_roma_id'].value;
    this.no_roma_found = false;
    this.data.getRomaInfo(roma_id).subscribe(
      data => {
        this.roma_loading = false;
        controls['dp_hkid'].setValue(data.hkid)
        controls['dp_roma_full_name'].setValue(data.roma_full_name);
        if (data.hkid === null) {
          this.no_roma_found = true;
        }
      },
      error => {
        this.roma_loading = false;
        this.utils.promptError(error, 'Cannot seach ROMA info');
      }
    )
    // let dpData = this.data.getDP(roma_id);
    // let hkid = dpData['dp_hkid'];
    // let fullName = dpData['dp_full_name'];
    // controls['dp_hkid'].setValue(hkid);
    // controls['dp_full_name'].setValue(fullName);
  }
  canGetRomaInfo() {
    return this.canEdit ? (this.form.controls['oa_need_dp'].value ? this.form.controls['dp_roma_id'].value : false) : false
  }

  doWinLoginChange() {
    let controls = this.form.controls;
    let ad_windows_login_name = controls['ad_windows_login_name'].value;
    this.winNameEvent.emit(ad_windows_login_name);
  }

  doNotesAccChange() {
    let controls = this.form.controls;
    let ln_first_name = controls['ln_first_name'].value;
    let ln_middle_name = controls['ln_middle_name'].value;
    let ln_last_name = controls['ln_last_name'].value;
    // let ln_mail = ln_first_name + ' ' + ln_middle_name + ' ' + ln_last_name
    let ln_mail = [ln_first_name, ln_middle_name, ln_last_name].join(' ');
    controls['ln_lotus_notes_mail_name'].patchValue(ln_mail);
    this.notesNameEvent.emit(ln_mail);
  }

  getBasicUserInfoControl() {
    return this.viewContainerRef['_data'].componentView.component.viewContainerRef['_view'].component['basicUserInfo'].form.controls;
  }

  doWinChg() {
    let sysControls = this.form.controls;
    let is_win = sysControls['oa_need_windows_login'].value;
    this.setWinValues(is_win);
  }

  doNotesChg() {
    let sysControls = this.form.controls;
    let is_notes = sysControls['oa_need_lotus_notes'].value;
    this.setNotesValues(is_notes);
  }

  doDPChg() {
    let sysControls = this.form.controls;
    let is_dp = sysControls['oa_need_dp'].value;
    this.setDPValues(is_dp);
  }

  doJJOChg() {
    let basicControls = this.basicControls;
    let sysControls = this.form.controls;
    let is_jjo = sysControls['oa_need_jjo'].value;
    this.setJJOValues(is_jjo);
  }

  setWinValues(isSet: boolean) {
    let sysControls = this.form.controls;
    if (isSet) {
      let basicFirstName = this.basicControls['given_name'].value;
      let basicSurname = this.basicControls['surname'].value;
      let basicPreName = this.basicControls['prefered_name'].value;
      let comLoginId = this.genLoginName(basicFirstName, basicSurname, basicPreName);
      let basicSurnameChg = basicSurname.substring(0, 1).toUpperCase() + basicSurname.substring(1).toLowerCase();

      // if (!sysControls['ad_location'].value) sysControls['ad_location'].patchValue(this.ad_locations[0]);
      if (!sysControls['ad_ou'].value) sysControls['ad_ou'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ad_locations));
      if (!sysControls['ad_windows_login_password'].value) sysControls['ad_windows_login_password'].patchValue(this.password);
      if (!sysControls['ad_windows_login_name'].value) sysControls['ad_windows_login_name'].patchValue(comLoginId);
      if (!sysControls['ad_windows_first_name'].value) sysControls['ad_windows_first_name'].patchValue(basicFirstName);
      if (!sysControls['ad_windows_last_name'].value) sysControls['ad_windows_last_name'].patchValue(basicSurnameChg);
    } else {
      // sysControls['ad_location'].patchValue("");
      // sysControls['ad_ou'].patchValue(null);
      sysControls['ad_windows_login_password'].patchValue("");
      sysControls['ad_windows_login_name'].patchValue("");
      sysControls['ad_windows_first_name'].patchValue("");
      sysControls['ad_windows_last_name'].patchValue("");
    }
    this.doWinLoginChange();
  }

  setNotesValues(isSet: boolean) {
    let sysControls = this.form.controls;
    if (isSet) {
      let basicFirstName = this.basicControls['given_name'].value;
      let basicSurname = this.basicControls['surname'].value;
      let basicSurnameChg = basicSurname.substring(0, 1).toUpperCase() + basicSurname.substring(1).toLowerCase();

      if (!sysControls['ln_account_type'].value) sysControls['ln_account_type'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_account_types));
      // if (!sysControls['ln_account_type'].value) sysControls['ln_account_type'].patchValue(null);
      if (!sysControls['ln_mps_range'].value) sysControls['ln_mps_range'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_mps_ranges));
      if (!sysControls['ln_is_gcn_user'].value) sysControls['ln_is_gcn_user'].patchValue(false);
      if (!sysControls['ln_is_contractor'].value) sysControls['ln_is_contractor'].patchValue(false);
      if (!sysControls['ln_is_confidential_mail_user'].value) sysControls['ln_is_confidential_mail_user'].patchValue(false);
      if (!sysControls['ln_mail_system'].value) sysControls['ln_mail_system'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_mail_systems));
      if (!sysControls['ln_mail_server'].value) sysControls['ln_mail_server'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_mail_servers));
      if (!sysControls['ln_mail_file_owner'].value) sysControls['ln_mail_file_owner'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_mail_file_owner_accesss));
      if (!sysControls['ln_mail_template'].value) sysControls['ln_mail_template'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_mail_file_templates));
      if (!sysControls['ln_mail_domain'].value) sysControls['ln_mail_domain'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_mail_domains));
      if (!sysControls['ln_client_license'].value) sysControls['ln_client_license'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_client_licenses));
      // if (!sysControls['ln_internet_mail_user'].value) sysControls['ln_internet_mail_user'].patchValue(this.ln_internet_mail_users[0]);
      if (!sysControls['ln_is_internet_mail_user'].value) sysControls['ln_is_internet_mail_user'].patchValue(false);
      if (!sysControls['ln_is_inote_user'].value) sysControls['ln_is_inote_user'].patchValue(false);
      if (!sysControls['ln_license_type'].value) sysControls['ln_license_type'].patchValue(this.utils.getDefaultValueFromSelectItem(this.ln_license_types));
      if (!sysControls['ln_notes_password'].value) sysControls['ln_notes_password'].patchValue(this.password);
      if (!sysControls['ln_first_name'].value) sysControls['ln_first_name'].patchValue(basicFirstName);
      if (!sysControls['ln_last_name'].value) sysControls['ln_last_name'].patchValue(basicSurnameChg);
      // if (!sysControls['ln_database_quota'].value) sysControls['ln_database_quota'].enable();
      // if (!sysControls['ln_warning_threshold'].value) sysControls['ln_warning_threshold'].enable();
      // if (!sysControls['ln_set_database_quota'].value) sysControls['ln_set_database_quota'].patchValue(true);
      // if (!sysControls['ln_set_warning_threshold'].value) sysControls['ln_set_warning_threshold'].patchValue(true);
    } else {
      sysControls['ln_account_type'].patchValue(null);
      sysControls['ln_mps_range'].patchValue(null);
      sysControls['ln_is_gcn_user'].patchValue(false);
      sysControls['ln_is_contractor'].patchValue(false);
      sysControls['ln_is_confidential_mail_user'].patchValue(false);
      sysControls['ln_mail_system'].patchValue(null);
      sysControls['ln_mail_server'].patchValue(null);
      sysControls['ln_mail_file_owner'].patchValue(null);
      sysControls['ln_mail_template'].patchValue(null);
      sysControls['ln_mail_domain'].patchValue(null);
      sysControls['ln_client_license'].patchValue(null);
      // sysControls['ln_internet_mail_user'].patchValue("");
      sysControls['ln_is_internet_mail_user'].patchValue(false);
      sysControls['ln_is_inote_user'].patchValue(false);
      sysControls['ln_license_type'].patchValue(null);
      sysControls['ln_notes_password'].patchValue("");
      sysControls['ln_first_name'].patchValue("");
      sysControls['ln_last_name'].patchValue("");;
      sysControls['ln_short_name'].patchValue("");
      sysControls['ln_lotus_notes_mail_name'].patchValue("");
    }
    this.doNotesAccChange();
  }

  setDPValues(isSet: boolean) {
    let sysControls = this.form.controls;
    if (isSet) {
      let basicFirstName = this.basicControls['given_name'].value;
      let basicSurname = this.basicControls['surname'].value;
      let basicPreName = this.basicControls['prefered_name'].value;
      let basicSurnameChg = basicSurname.substring(0, 1).toUpperCase() + basicSurname.substring(1).toLowerCase();
      let comLoginId = this.genLoginName(basicFirstName, basicSurname, basicPreName);

      // if (!sysControls['dp_rank_code'].value) sysControls['dp_rank_code'].patchValue(this.dp_rank_codes[0]);
      if (!sysControls['dp_rank_code'].value) sysControls['dp_rank_code'].patchValue(this.utils.getDefaultValueFromSelectItem(this.dp_rank_codes));
      // if (!sysControls['dp_staff_code'].value) sysControls['dp_staff_code'].patchValue(this.dp_staff_codes[0]);
      if (!sysControls['dp_staff_code'].value) sysControls['dp_staff_code'].patchValue(this.utils.getDefaultValueFromSelectItem(this.dp_staff_codes));
      // if (!sysControls['dp_emp_type'].value) sysControls['dp_emp_type'].patchValue(this.dp_emp_types[0]);
      if (!sysControls['dp_emp_type'].value) sysControls['dp_emp_type'].patchValue(this.utils.getDefaultValueFromSelectItem(this.dp_emp_types));
      if (!sysControls['dp_dep_id'].value) sysControls['dp_dep_id'].patchValue("JUD");
      if (!sysControls['dp_login_id'].value) sysControls['dp_login_id'].patchValue(comLoginId);
      if (!sysControls['dp_first_name'].value) sysControls['dp_first_name'].patchValue(basicFirstName);
      if (!sysControls['dp_last_name'].value) sysControls['dp_last_name'].patchValue(basicSurnameChg);
    } else {
      sysControls['dp_rank_code'].patchValue(null);
      sysControls['dp_staff_code'].patchValue(null);
      sysControls['dp_emp_type'].patchValue(null);
      sysControls['dp_dep_id'].patchValue("");
      sysControls['dp_login_id'].patchValue("");
      sysControls['dp_first_name'].patchValue("");
      sysControls['dp_last_name'].patchValue("");
    }
  }

  setJJOValues(isSet: boolean) {
    let sysControls = this.form.controls;
    if (isSet) {
      let basicFirstName = this.basicControls['given_name'].value;
      let basicSurname = this.basicControls['surname'].value;
      let basicPreName = this.basicControls['prefered_name'].value;
      let basicSurnameChg = basicSurname.substring(0, 1).toUpperCase() + basicSurname.substring(1).toLowerCase();
      let comLoginId = this.genLoginName(basicFirstName, basicSurname, basicPreName);

      if (!sysControls['jjo_mail_domain'].value) sysControls['jjo_mail_domain'].patchValue(this.utils.getDefaultValueFromSelectItem(this.jjo_mail_domains));
      if (!sysControls['jjo_login_id'].value) sysControls['jjo_login_id'].patchValue(comLoginId);
      if (!sysControls['jjo_first_name'].value) sysControls['jjo_first_name'].patchValue(basicFirstName);
      if (!sysControls['jjo_last_name'].value) sysControls['jjo_last_name'].patchValue(basicSurnameChg);
      if (!sysControls['jjo_emp_type'].value) sysControls['jjo_emp_type'].patchValue(this.utils.getDefaultValueFromSelectItem(this.dp_emp_types));

    } else {
      sysControls['jjo_mail_domain'].patchValue(null);
      sysControls['jjo_login_id'].patchValue("");
      sysControls['jjo_first_name'].patchValue("");
      sysControls['jjo_last_name'].patchValue("");
      sysControls['jjo_emp_type'].patchValue(null);
    }
  }

  doLnDBCheck(event) {
    let ln_database_quota = this.form.controls['ln_database_quota'];
    if (event) {
      // ln_database_quota.enable();
    } else {
      // ln_database_quota.disable();
      ln_database_quota.setValue(null);
    }
  }

  doLnWarnCheck(event) {
    let ln_warning_threshold = this.form.controls['ln_warning_threshold'];
    if (event) {
      // ln_warning_threshold.enable();
    } else {
      // ln_warning_threshold.disable();
      ln_warning_threshold.patchValue(null);
    }
  }

  markFormDirty(event: any) {
    this.form.markAsDirty();
  }

  canSelectInterfaceTab(tabName: string) {
    if (this.canEdit) {
      if (this.request && 'original_user_info' in this.request) {
        let original_value: boolean = this.request['original_user_info'][tabName];
        return (original_value) ? false : true;
      }
      return true;
    }
    return false;
  }

  onLnShortnameChange() {
    this.form.controls['ln_internet_address'].patchValue(this.form.controls['ln_short_name'].value);
  }
}
