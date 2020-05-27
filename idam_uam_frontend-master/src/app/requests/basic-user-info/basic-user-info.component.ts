import { Component, OnInit, Input } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ValidatorFn } from '@angular/forms';
import { CommunicationService } from '../../judCommon/communication.service';
import { FormatDatePipe } from '../../judCommon/formatDate.pipe';
import { Section, Rank } from '../../models/models';
import { DataService } from '../../judCommon/data.service';
import { UtilService } from '../../judCommon/util.service';
// import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-basic-user-info',
  templateUrl: './basic-user-info.component.html',
  styleUrls: ['./basic-user-info.component.css']
})

export class BasicUserInfoComponent implements OnInit {

  @Input() parentForm: FormGroup;
  @Input() groupName: string;
  @Input() showContactInfo: boolean = true;
  @Input() canEdit: boolean = false;

  formName: string;
  form: FormGroup;
  win_login: string;
  notes_acc: string;

  suggestedSection: Section[];
  private _section: string;
  @Input() set section(section: Section) {
    if ('section' in this.form.controls) {
      this.form.controls['section'].patchValue(section);
    }
  }

  suggestedRank: Rank[] = [];
  private _rank: Rank;
  @Input() set rank(rank: Rank) {
    this._rank = rank;
    this.form.controls['master_rank'].patchValue(rank);
  }

  suggestedSubRank: Rank[] = [];
  private _subrank: Rank;
  @Input() set substantive_rank(rank: Rank) {
    this._subrank = rank;
    this.form.controls['substantive_rank'].patchValue(rank);
  }

  titles: any[] = [{ id: 1, value: 'Mr' }, { id: 2, value: 'Mrs' }, { id: 3, value: 'Miss' }, { id: 4, value: 'Dr' }];
  // ranks: any[] = [{ id: 1, value: 'Manager' }, { id: 2, value: 'Engineer' }, { id: 3, value: 'Programmer' }];
  // sub_ranks: any[] = [{ id: 1, value: 'CSA' }, { id: 2, value: 'CSSA' }, { id: 3, value: 'CP' }];
  acc_types: any[] = [{ id: 1, value: 'JJO' }, { id: 2, value: 'Non-JJO' }, { id: 3, value: 'Special Account' }];
  // sections: any[] = [{ id: 1, value: 'ITOO' }, { id: 2, value: 'ITOT' }, { id: 3, value: 'Finance' }];

  _validateDateRange(startfield: string, endfield: string): ValidatorFn {
    return (form: FormGroup): { [key: string]: any } | null => {
      const from = this.form.controls[startfield];
      const to = this.form.controls[endfield];
      if (from.valid && to.valid && to.value != null && from.value != null) {
        const from_value = (typeof from.value == 'string' && from.value) ? (new FormatDatePipe().transform(from.value)) : from.value;
        const to_value = (typeof to.value == 'string' && to.value) ? (new FormatDatePipe().transform(to.value)) : to.value;
        if ((from_value > to_value) && (from_value != to_value) && (from_value) && (to_value)) {
          return { 'date_range_error': true };
        } else {
          return null;
        }
      }
      return null;
    }
  }

  constructor(private _fb: FormBuilder, private comm: CommunicationService, public data: DataService, private util: UtilService) { }

  ngOnInit() {
    this.formName = `${this.groupName}Form`;
    this.form = this._fb.group({
      account_effective_start_date: ['', [Validators.required]],
      account_effective_end_date: [''],
      title: ['', [Validators.required]],
      given_name: ['', [Validators.required]],
      surname: ['', [Validators.required]],
      prefered_name: [''],
      given_name_chinese: [''],
      surname_chinese: [''],
      post_title: ['', [Validators.required]],
      // rank: [''],
      master_rank: [null],
      // substantive_rank: [''],
      substantive_rank: [null],
      section: [null, [Validators.required]],
      account_type: [''],
      installation_contact_person: [''],
      installation_contact_phone_no: [''],
    });
    if (!this.data.canSelectSection()) {
      this.form.removeControl('section')
    }
    this.form.setValidators(this._validateDateRange('account_effective_start_date', 'account_effective_end_date'));
    this.parentForm.addControl(this.formName, this.form);
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      let controls = this.form.controls;
      // if (!controls['section'].value) controls['section'].setValue(this.sections[0]);
      if (!controls['title'].value) controls['title'].setValue(this.titles[0]);
      // if (!controls['rank'].value) controls['rank'].setValue(this.ranks[0]);
      // if (!controls['substantive_rank'].value) controls['substantive_rank'].setValue(this.sub_ranks[0]);
      if (!controls['account_type'].value) controls['account_type'].setValue(this.acc_types[0]);
      if (!controls['account_effective_start_date'].value) controls['account_effective_start_date'].setValue(new Date());
    }, 500);
  }

  onNameChanged(field_name: string) {
    let controls = this.form.controls;
    // controls['surname'].setValue(controls['surname'].value.toUpperCase());
    // let tmpname = [controls['given_name'].value, controls['surname'].value];
    controls[field_name].setValue(this.util.formatName(controls[field_name].value));
    //this.comm.setUserName(tmpname);
  }

  // onSurnameInput() {
  //   let controls = this.form.controls;
  //   controls['surname'].setValue(controls['surname'].value.toUpperCase());
  // }

  doNotesNameEvent($event) {
    this.notes_acc = $event;
  }

  doWinName($event) {
    this.win_login = $event;
  }

  clearSection(event: any) {
    this.form.controls['section'].patchValue(null);
    this.form.controls['section'].markAsDirty();
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
        // this.messageService.add({severity: 'error', summary: 'Cannot get sections', detail: this.util.parseError(error)})
        this.util.promptError(error, 'Cannot search sections');
        this.suggestedSection = [];
        // console.log(error);
      }
    )
  }

  clearRank(event: any, field_name: string) {
    if (field_name in this.form.controls) {
      this.form.controls[field_name].patchValue(null);
      this.form.controls[field_name].markAsDirty();
    }
  }

  private _updateRanksSuggestion(data: Rank[]) {
    let suggestion: Rank[] = [];
    data.forEach((currentValue, idx, arr) => {
      suggestion.push(currentValue);
    })
    return suggestion;
  }
  searchRanks(event: any, field_name: string) {
    let query = event.query;
    let entered: string = event.query;
    this.data.searchRanks(entered).subscribe(
      data => {
        if (field_name == 'master_rank') {
          this.suggestedRank = this._updateRanksSuggestion(data);
        } else {
          this.suggestedSubRank = this._updateRanksSuggestion(data);
        }
      }, error => {
        // this.messageService.add({severity: 'error', summary: 'Cannot get rank', detail: this.util.parseError(error)})
        this.util.promptError(error, 'Cannot search ranks');
        if (field_name == 'master_rank') {
          this.suggestedRank = [];
        } else {
          this.suggestedSubRank = [];
        }
        // console.log(error);
      }
    )
  }
}
