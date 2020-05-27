import { Component } from '@angular/core';
import { DataService } from './judCommon/data.service';
import { LoginUserInfo } from './models/models';
import { UtilService } from './judCommon/util.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'uat-frontend-primeng';
  jud_icon_path = 'assets/img/logo.jpg';

  current_user: LoginUserInfo;
  constructor(public data: DataService, private utils: UtilService) { }

  ngOnInit(): void {
    this.data.getCurrentUserInfo().subscribe(
      data => {
        this.data.current_user = data;
        if (data.username === null) {
          window.location.href = `${this.data.API_URL}/auth/sso/`;
        }
        this.current_user = data;
      },
      error => {
        alert(error.message);
        // this.utils.promptError(error, 'Cannot load user info');
        console.log(error);
      }
    );
  }

}
