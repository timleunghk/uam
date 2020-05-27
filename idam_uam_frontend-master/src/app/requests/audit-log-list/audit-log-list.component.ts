import { Component, OnInit, Input } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { UtilService } from '../../judCommon/util.service';

@Component({
  selector: 'app-audit-log-list',
  templateUrl: './audit-log-list.component.html',
  styleUrls: ['./audit-log-list.component.css']
})

export class AuditLogListComponent implements OnInit {

  private _request_id: string;
  @Input() set request_id(val: string) {
    this._request_id = val;
    this.logs = [];
    this.data.getRequestAuditlog(this.request_id).subscribe(
      data => this.logs = data,
      error => {
        this.utils.promptError(error, 'Cannot search Audit Log');
        console.log(error);
      }
    )
  }

  get request_id(): string {
    return this._request_id;
  }

  logs: any;

  constructor(private data: DataService, private utils: UtilService) { }

  ngOnInit() { }

}
