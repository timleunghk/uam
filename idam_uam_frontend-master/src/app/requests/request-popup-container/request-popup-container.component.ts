import { Component, OnInit, Input, ViewChild , ViewContainerRef } from '@angular/core';
import { DataService } from '../../judCommon/data.service';
import { BaseRequest } from '../../models/models';
import { CommunicationService } from '../../judCommon/communication.service';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { JudDialogComponent } from '../../judCommon/jud-dialog.component';

@Component({
  selector: 'app-request-popup-container',
  templateUrl: './request-popup-container.component.html',
  styleUrls: ['./request-popup-container.component.css']
})

export class RequestPopupContainerComponent implements OnInit {

  @ViewChild('judDialog', { static: true }) judDialog: JudDialogComponent;
  header: string = '';
  content_show_map = {};
  request: BaseRequest;
  request_id: string;
  id: Number;
  tabActiveIndex: number = 1;
  _display: boolean = false;
  _in_request: BaseRequest;
  user_id: string;
  uam_id: string;
  uam_id_string: string;

  set display(val: boolean) {
    this._display = val;
    if (val) {
      this.tabActiveIndex = 0;
    }
  }

  get display(): boolean {
    return this._display;
  }


  @Input() set in_request(val: BaseRequest) {
    this._in_request = val;
    let id = this._in_request.id;
    this.data.getRequest(id).subscribe(
      data => {
        this.request = data;
        this.content_show_map = {};
        this.build_content_show_map();
        this.request_id = data['request_id'];
        this.id = data['id'];
        this.uam_id = data['uam_id'];
        this.user_id = data['related_user'];
        this.uam_id_string = ( this.uam_id )? '\u00A0\u00A0\u00A0,\u00A0\u00A0\u00A0UAM ID : ' + this.uam_id  +'('+ this.user_id+')': '' ;
        this.display = true;
      },error => {
        this.display = false;
        // this.judDialog.showDialog('Error', 'Open Failed : ' + error.message, 'error', 'info');        
        this.judDialog.promptError(error, 'Open Failed');
      }
    )
  };
 
/*
  @Input() set in_request(val: BaseRequest) {
    this._in_request = val;
    let id = this._in_request.id;
    this.getRequest(id);
  };  

  async getRequest(id) {
    try {
      let data = await this.data.getRequestAsync(id);
      this.request = data;
      this.content_show_map = {};
      this.build_content_show_map();
      this.request_id = data['request_id'];
      this.id = data['id'];
      this.uam_id = data['uam_id'];
      this.user_id = data['related_user'];
      this.uam_id_string = (this.uam_id) ? '\u00A0\u00A0\u00A0,\u00A0\u00A0\u00A0UAM ID : ' + this.uam_id + '(' + this.user_id + ')' : '';
      this.display = true;
    } catch (error) {
      this.display = false;
      this.judDialog.showDialog('Error', 'Open Failed : ' + error.message, 'error', 'info');
    }
  }  
  */

  constructor(private data: DataService, private comm: CommunicationService, private rout: ActivatedRoute, private location: Location, private viewContainerRef: ViewContainerRef  ) {    
    this.comm.objHeader$.subscribe( 
      data => this.header = data + '  ---- ' + ' Request ID  :  ' + this.request_id + ' (' + this.id + ')'   + this.uam_id_string
    );  
  }
  
  ngOnInit() {

  }

  private build_content_show_map() {    
    if (this.request.hasOwnProperty('resourcetype')) {
      //this.content_show_map[`${this.request['resourcetype']}_${this.request['status']}`] = true;
      this.content_show_map['resourcetype'] = this.request['resourcetype'];
      this.content_show_map['status'] = this.request['status'];
    }
  }

  canShow(request_resourcetype, request_status): boolean {    
    return (request_status.indexOf(this.content_show_map['status']) > -1) 
      && (request_resourcetype.indexOf(this.content_show_map['resourcetype']) > -1);
  }

  onChildClose(event) {
    this.display = false;
  }

  onHide() {
    this.content_show_map = {};
  }

}

