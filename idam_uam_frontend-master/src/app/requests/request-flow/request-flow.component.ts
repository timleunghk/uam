import { Component, OnInit, Input } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-request-flow',
  templateUrl: './request-flow.component.html',
  styleUrls: ['./request-flow.component.css']
})

export class RequestFlowComponent implements OnInit {

  @Input() set request(val: any) {
    this.setData(val)
  }

  aIndex: number = 0;
  items: MenuItem[] = [];

  constructor(private data: DataService) { }

  ngOnInit() {

  }

  setData(val) {
    let status = [
      { 0: 'New Request' },
      { 1: 'Pending For ITOO\'s review' },
      { 2: 'Pending For ITOT\'s review' },
      { 3: 'Confirmed by HelpDesk' },
      { 4: 'Rejected by ITOO' },
      { 5: 'Rejected by ITOT' },
      { 6: 'Setup Completed' },
      { 7: 'User Acknowledged' },
      { 8: 'Reset Password Completed' },
      { 9: 'Disable Account Completed' },
      { 10: 'Re-Enable Account Completed' },
      { 11: 'Delete Account Completed' },
      { 12: 'Update Account Completed' },
    ];
    let request_status = val['request_status_name'];
    let request_type = val['resourcetype'];

    let request_code = Number(val['status']);
    this.items = [];

    let tmpStep = null;
    let createAccNormal = [0, 1, 2, 3, 6, 7];
    let createAccRejItoo = [0, 1, 4];
    let createAccRejItot = [0, 1, 2, 5];
    let updateAccNormal = [0, 1, 2, 12];
    let updateAccRejItoo = [0, 1, 4];
    let updateAccRejItot = [0, 1, 2, 5];

    if (request_type == "CreateAccountRequest") {
      if (request_code == 4) {
        tmpStep = createAccRejItoo;
      } else if (request_code == 5) {
        tmpStep = createAccRejItot;
      } else {
        tmpStep = createAccNormal;
      }
    } else if (request_type == "UpdateAccountRequest") {
      if (request_code == 4) {
        tmpStep = updateAccRejItoo;
      } else if (request_code == 5) {
        tmpStep = updateAccRejItot;
      } else {
        tmpStep = updateAccNormal;
      }
    }

    if (tmpStep != null) {
      for (var item of tmpStep) {
        let name = status[item][item];
        this.items.push({ label: name });
      }
      //console.log(request_type);
      //console.log(request_code);
      this.aIndex = tmpStep.indexOf(request_code);
    }

  }

}



