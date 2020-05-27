import { Component, OnInit, ViewChild } from '@angular/core';
import { BaseRequest } from '../../models/models';
import { CommunicationService } from '../../judCommon/communication.service';
import { RequestsDetailNewAccountComponent } from '../requests-detail-account-new/requests-detail-account-new.component';

@Component({
  selector: 'app-request-new-container',
  templateUrl: './request-new-container.component.html',
  styleUrls: ['./request-new-container.component.css'],
  providers: [CommunicationService],
})

export class RequestNewContainerComponent implements OnInit {


  @ViewChild('detail', { static: true }) detail: RequestsDetailNewAccountComponent;
  request: BaseRequest;
  constructor(private comm: CommunicationService) {
    comm.objCompleted$.subscribe(
      data => {
        // this.request = { resourcetype: 'CreateAccountRequest'  , status: 0 } as BaseRequest;
        this.refreshNewScreen();
      }
    )
  }

  ngOnInit() {
    // this.request = { resourcetype: 'CreateAccountRequest'  , status: 0 } as BaseRequest;
    this.refreshNewScreen();
  }

  refreshNewScreen() {
    this.request = { resourcetype: 'CreateAccountRequest', status: 0, account_type: 2 } as BaseRequest;
    setTimeout(() => {
      if (!this.detail.canEdit) {
        this.detail.toggleEditMode();
        this.detail.onReset();
      }
    }, 200);

    // this.detail.toggleEditMode();
    // console.log(this.detail.canEdit)
  }

}


