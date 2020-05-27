import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DataService } from '../../judCommon/data.service';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-requests-setup-complete',
  templateUrl: './requests-setup-complete.component.html',
  styleUrls: ['./requests-setup-complete.component.css'],
})

export class RequestsSetupCompleteComponent implements OnInit {

  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;
  requestId: string;
  uamId: string;
  winLogin: string;
  surname: string;
  givenName: string;
  rank: string;
  postTitle: string;
  intMail: string;
  notesMail: string;
  section: string;
  status_name: string;
  isShowButton: boolean = false;

  constructor(private data: DataService, private utils: UtilService, private route: ActivatedRoute) { }

  ngOnInit() { }

  ngAfterViewInit(): void {
    setTimeout(() => {
      let sId = this.route.snapshot.queryParamMap.get('id');
      if (sId != null && Number(sId)) {
        this.data.getRequest(Number(sId)).subscribe(
          data => {
            this.requestId = data['id'].toString();
            this.uamId = data['uam_id'];
            this.winLogin = data['ad_windows_login_name'];
            this.surname = data['surname'];
            this.givenName = data['given_name'];
            if (data['master_rank']) {
              this.data.getRank(data['master_rank']).subscribe(
                tmp_data => {
                  this.rank = tmp_data['display_text'];
                }
              )
            }
            this.postTitle = data['post_title'];
            this.intMail = data['intMail'];
            this.notesMail = data['ln_lotus_notes_mail_name'];
            this.section = data['section'] ? data['section']['code']: '';
            this.status_name = data['query_status_desc'];
            this.isShowButton = (data['status'] == 3);
          }, error => {
            // this.judDialog.showDialog('Search Error', this.utils.parseError(error), 'error', 'info');
            this.judDialog.promptError(error, 'Search Failed');
            console.log(error.message);
          }
        )
      }
    }, 500);
  }

  onClick() {
    let sId = this.route.snapshot.queryParamMap.get('id');
    if (sId != null && Number(sId)) {
      this.judDialog.showDialog('Information', 'The setup complete is submitting', 'wait', 'wait');
      this.data.setupComplete(Number(sId)).subscribe(
        data => {
          this.judDialog.showDialog('Information', 'The setup complete is submitted successfully', 'succ', 'info');
          this.isShowButton = false;
          this.status_name = 'Setup Completed';
        }, error => {
          // this.judDialog.showDialog('Error', this.utils.parseError(error), 'error', 'info');
          this.judDialog.promptError(error, 'Setup Failed');
        }
      )
    }
  }


}




