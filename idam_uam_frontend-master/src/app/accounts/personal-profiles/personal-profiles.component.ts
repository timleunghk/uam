import { Component, OnInit, } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DataService } from '../../judCommon/data.service';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-personal-profiles',
  templateUrl: './personal-profiles.component.html',
  styleUrls: ['./personal-profiles.component.css'],
})

export class PersonalProfilesComponent implements OnInit {

  uamId: string;
  winLogin: string;
  surname: string;
  givenName: string;
  rank: string;
  postTitle: string;
  intMail: string;
  notesMail: string;
  section: string;

  constructor(private data: DataService, private utils: UtilService, private route: ActivatedRoute) { }

  ngOnInit() { }

  ngAfterViewInit(): void {
    setTimeout(() => {
      let sId = this.route.snapshot.queryParamMap.get('id');
      if (sId != null && Number(sId)) {
        this.data.getPersonal(sId).subscribe(
          data => {
            this.uamId = data['uam_id'];
            this.winLogin = data['ad_windows_login_name'];
            this.surname = data['surname'];
            this.givenName = data['given_name'];
            this.rank = data['id'];
            this.postTitle = data['post_title'];
            this.intMail = data['intMail'];
            this.notesMail = data['ln_lotus_notes_mail_name'];
            this.section = data['section'];
          }, error => {
            this.utils.promptError(error, 'Cannot load personal profile');
            console.log(error.message);
          }
        )
      }
    }, 500);
  }

}


