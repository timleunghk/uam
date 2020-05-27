import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { MessageService } from 'primeng/api';
// import { utils } from 'protractor';
import { UtilService } from './util.service';
import { sum } from 'angular-pipes/utils/utils';

@Component({
  providers: [MessageService],
  selector: 'app-jud-dialog',
  template: `
  <p-toast id="toast-container" [modal]="false" position="center" [style]="{'width': '600px' }" [showTransitionOptions]="'0ms'"
  [hideTransitionOptions]="'0ms'"  [baseZIndex]="5000">
  <ng-template let-message pTemplate="message">
    <div style="margin-top: -20px;">
      <div style="text-align: left">
        <h1>{{message.summary}}</h1>
      </div>
      <div class="p-grid">
        <div style="transform: translateY(-10%); -webkit-transform: translateY(-10%); margin-left: 20px;margin-right: 20px;">
            <img [src]="'assets/img/'+ message.data['icon']+'.png'" style="width:60px;height:60px">
        </div>
        <div>
          <div style="display: table-cell ;vertical-align: middle ;text-align: left; width: 450px; height: 60px; -ms-word-wrap: break-word; "
            [innerHTML]="message.detail">
          </div>
        </div>
      </div>
      <hr>
      <div>
        <div style="display: table-cell ;vertical-align: middle ;text-align: right; width: 600px; height: 40px; ">
          <button pButton type="button" label="Yes" class="button_common" (click)="onDialogSubmit()" *ngIf="message.data['type'] =='confirmSub'"></button>
          <button pButton type="button" label="Yes" class="button_common" (click)="onDialogReject()" *ngIf="message.data['type'] =='confirmRej'"></button>
          <button pButton type="button" label="{{message.data['type'] =='info'?'Close':'No'}}" class="button_common" 
          (click)="onDialogNo(message.summary ,message.data['type'] =='info'?'Close':'No' )" 
          *ngIf="message.data['type'] !='wait'" >  
          </button>
        </div>
      </div>
    </div>
  </ng-template>
</p-toast>
<div class="overlay" *ngIf="showOverlay"><div>
`,
})

export class JudDialogComponent implements OnInit {

  @Output() submitEvent = new EventEmitter<string>();
  @Output() rejectEvent = new EventEmitter<string>();
  @Output() closeEvent = new EventEmitter<string>();
  showOverlay: boolean = false;

  constructor(private messageService: MessageService, private utils: UtilService) { }

  ngOnInit() { }

  onDialogNo(summary, messageType) {
    if (messageType.match('Close') != null && summary.match('Info') != null) {
      this.closeEvent.emit();
    }
    this.showOverlay = false;
    this.messageService.clear();
  }

  onDialogSubmit() {
    this.submitEvent.emit();
  }

  onDialogReject() {
    this.rejectEvent.emit();
  }

  showDialog(_summary: string, _detail: string, _icon: string, _type: string) {
    this.showOverlay = true;
    this.messageService.clear();
    this.messageService.add({
      severity: 'success',
      summary: _summary,
      detail: _detail,
      closable: false, sticky: true,
      data: { icon: _icon, type: _type },
    });
  }

  promptError(error: any, summary: string) {
    let msg = this.utils.parseError(error);
    this.showDialog(summary, msg, 'error', 'info');
  }
}
